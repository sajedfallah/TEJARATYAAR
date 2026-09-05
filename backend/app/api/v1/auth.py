from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.security import create_access_token, verify_telegram_init_data
from app.dependencies import get_current_user, get_db
from app.models import Role, User, UserStatus
from app.schemas import MeResponse, TelegramLoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/telegram", response_model=TokenResponse)
def telegram_login(payload: TelegramLoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    try:
        telegram_user = verify_telegram_init_data(payload.init_data)
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from None

    telegram_id = telegram_user.get("id")
    if telegram_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Telegram user id is missing")

    user = db.scalar(
        select(User)
        .options(selectinload(User.roles))
        .where(User.telegram_id == int(telegram_id))
    )
    if user is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This Telegram account has not been invited")
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User access is not active")

    user.last_active_at = datetime.now(timezone.utc)
    user.first_name = telegram_user.get("first_name") or user.first_name
    user.last_name = telegram_user.get("last_name") or user.last_name
    user.username = telegram_user.get("username") or user.username
    db.commit()

    roles = [role.code for role in user.roles]
    return TokenResponse(access_token=create_access_token(str(user.id), roles))


@router.get("/me", response_model=MeResponse)
def me(user: User = Depends(get_current_user)) -> MeResponse:
    permissions = sorted({permission.code for role in user.roles for permission in role.permissions})
    return MeResponse(
        id=user.id,
        telegram_id=user.telegram_id,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        is_superuser=user.is_superuser,
        roles=[role.code for role in user.roles],
        permissions=permissions,
    )
