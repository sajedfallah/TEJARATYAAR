import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.security import create_access_token, verify_telegram_init_data
from app.dependencies import get_current_user, get_db, require_permission
from app.models import CustomerContact, Invite, Role, User, UserStatus
from app.operational_models import CustomerUserLink
from app.operational_schemas import InviteActivate, InviteCreate, InviteCreated
from app.schemas import TokenResponse
from app.services.audit import write_audit

router = APIRouter(tags=["invites"])


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


@router.post("/management/invites", response_model=InviteCreated, status_code=status.HTTP_201_CREATED)
def create_invite(
    payload: InviteCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(require_permission("invite.manage")),
) -> InviteCreated:
    role = db.scalar(select(Role).where(Role.code == payload.role_code))
    if role is None:
        raise HTTPException(status_code=400, detail="Unknown role")
    if payload.role_code == "customer" and payload.customer_id is None:
        raise HTTPException(status_code=400, detail="Customer invite requires customer_id")
    if payload.role_code != "customer" and payload.customer_id is not None:
        raise HTTPException(status_code=400, detail="Only customer invites may include customer_id")

    raw_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=payload.expires_in_hours)
    invite = Invite(
        token_hash=_hash_token(raw_token),
        role_code=payload.role_code,
        customer_id=payload.customer_id,
        expires_at=expires_at,
    )
    db.add(invite)
    db.flush()
    write_audit(
        db,
        actor_user_id=actor.id,
        action="invite.created",
        entity_type="invite",
        entity_id=str(invite.id),
        metadata={"role_code": payload.role_code, "customer_id": payload.customer_id, "expires_at": expires_at},
    )
    db.commit()
    return InviteCreated(id=invite.id, token=raw_token, expires_at=expires_at)


@router.post("/auth/activate-invite", response_model=TokenResponse)
def activate_invite(payload: InviteActivate, db: Session = Depends(get_db)) -> TokenResponse:
    try:
        telegram_user = verify_telegram_init_data(payload.init_data)
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from None

    now = datetime.now(timezone.utc)
    invite = db.scalar(select(Invite).where(Invite.token_hash == _hash_token(payload.token)).with_for_update())
    if invite is None:
        raise HTTPException(status_code=404, detail="Invite not found")
    if invite.revoked_at is not None or invite.used_at is not None or invite.expires_at <= now:
        raise HTTPException(status_code=410, detail="Invite is expired, revoked, or already used")

    role = db.scalar(select(Role).options(selectinload(Role.permissions)).where(Role.code == invite.role_code))
    if role is None:
        raise HTTPException(status_code=409, detail="Invite role is not configured")

    telegram_id = int(telegram_user["id"])
    user = db.scalar(select(User).options(selectinload(User.roles)).where(User.telegram_id == telegram_id))
    if user is None:
        user = User(
            telegram_id=telegram_id,
            first_name=telegram_user.get("first_name") or "Telegram User",
            last_name=telegram_user.get("last_name"),
            username=telegram_user.get("username"),
            status=UserStatus.ACTIVE,
            last_active_at=now,
        )
        db.add(user)
        db.flush()
    elif user.status != UserStatus.ACTIVE:
        raise HTTPException(status_code=403, detail="User is not active")

    if role not in user.roles:
        user.roles.append(role)

    if invite.role_code == "customer":
        existing_link = db.scalar(select(CustomerUserLink).where(CustomerUserLink.user_id == user.id))
        if existing_link is not None and existing_link.customer_id != invite.customer_id:
            raise HTTPException(status_code=409, detail="Telegram account is already linked to another customer")
        if existing_link is None:
            contact = CustomerContact(
                customer_id=invite.customer_id,
                name=" ".join(filter(None, [telegram_user.get("first_name"), telegram_user.get("last_name")])) or "Telegram Contact",
                telegram_id=telegram_id,
                is_active=True,
            )
            db.add(contact)
            db.flush()
            db.add(CustomerUserLink(user_id=user.id, customer_id=invite.customer_id, contact_id=contact.id))

    invite.used_at = now
    write_audit(
        db,
        actor_user_id=user.id,
        action="invite.activated",
        entity_type="invite",
        entity_id=str(invite.id),
        metadata={"role_code": invite.role_code, "customer_id": invite.customer_id, "telegram_id": telegram_id},
    )
    db.commit()

    roles = [item.code for item in user.roles]
    return TokenResponse(access_token=create_access_token(str(user.id), roles))
