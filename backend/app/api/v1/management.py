from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_permission
from app.models import Customer, CustomerContact, Team, User
from app.operational_models import CaseType, CustomsOffice
from app.operational_schemas import (
    CaseTypeCreate,
    CaseTypeRead,
    ContactCreate,
    ContactRead,
    CustomerCreate,
    CustomerRead,
    CustomsOfficeCreate,
    CustomsOfficeRead,
    TeamCreate,
    TeamRead,
    UserListItem,
)
from app.services.audit import write_audit

router = APIRouter(prefix="/management", tags=["management"])


@router.get("/users", response_model=list[UserListItem])
def list_users(
    db: Session = Depends(get_db),
    actor: User = Depends(require_permission("user.manage")),
) -> list[UserListItem]:
    users = db.scalars(select(User).order_by(User.first_name, User.last_name)).unique().all()
    return [
        UserListItem(
            id=user.id,
            telegram_id=user.telegram_id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            status=user.status.value,
            roles=[role.code for role in user.roles],
        )
        for user in users
    ]


@router.post("/customers", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
def create_customer(
    payload: CustomerCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(require_permission("customer.manage")),
) -> Customer:
    customer = Customer(**payload.model_dump())
    db.add(customer)
    db.flush()
    write_audit(db, actor_user_id=actor.id, action="customer.created", entity_type="customer", entity_id=str(customer.id))
    db.commit()
    db.refresh(customer)
    return customer


@router.get("/customers", response_model=list[CustomerRead])
def list_customers(
    db: Session = Depends(get_db),
    actor: User = Depends(require_permission("customer.manage")),
) -> list[Customer]:
    return list(db.scalars(select(Customer).where(Customer.is_active.is_(True)).order_by(Customer.name)).all())


@router.post("/customers/{customer_id}/contacts", response_model=ContactRead, status_code=status.HTTP_201_CREATED)
def create_contact(
    customer_id: UUID,
    payload: ContactCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(require_permission("customer.manage")),
) -> CustomerContact:
    customer = db.get(Customer, customer_id)
    if customer is None or not customer.is_active:
        raise HTTPException(status_code=404, detail="Customer not found")
    contact = CustomerContact(customer_id=customer_id, **payload.model_dump())
    db.add(contact)
    db.flush()
    write_audit(db, actor_user_id=actor.id, action="customer_contact.created", entity_type="customer_contact", entity_id=str(contact.id), metadata={"customer_id": customer_id})
    db.commit()
    db.refresh(contact)
    return contact


@router.get("/customers/{customer_id}/contacts", response_model=list[ContactRead])
def list_contacts(
    customer_id: UUID,
    db: Session = Depends(get_db),
    actor: User = Depends(require_permission("customer.manage")),
) -> list[CustomerContact]:
    return list(db.scalars(select(CustomerContact).where(CustomerContact.customer_id == customer_id, CustomerContact.is_active.is_(True)).order_by(CustomerContact.name)).all())


@router.post("/teams", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
def create_team(
    payload: TeamCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(require_permission("team.manage")),
) -> Team:
    if payload.supervisor_id and db.get(User, payload.supervisor_id) is None:
        raise HTTPException(status_code=400, detail="Supervisor not found")
    team = Team(**payload.model_dump())
    db.add(team)
    db.flush()
    write_audit(db, actor_user_id=actor.id, action="team.created", entity_type="team", entity_id=str(team.id))
    db.commit()
    db.refresh(team)
    return team


@router.get("/teams", response_model=list[TeamRead])
def list_teams(
    db: Session = Depends(get_db),
    actor: User = Depends(require_permission("team.manage")),
) -> list[Team]:
    return list(db.scalars(select(Team).where(Team.is_active.is_(True)).order_by(Team.name)).all())


@router.post("/customs-offices", response_model=CustomsOfficeRead, status_code=status.HTTP_201_CREATED)
def create_customs_office(
    payload: CustomsOfficeCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(require_permission("customs.manage")),
) -> CustomsOffice:
    office = CustomsOffice(**payload.model_dump())
    db.add(office)
    db.flush()
    write_audit(db, actor_user_id=actor.id, action="customs_office.created", entity_type="customs_office", entity_id=str(office.id))
    db.commit()
    db.refresh(office)
    return office


@router.get("/customs-offices", response_model=list[CustomsOfficeRead])
def list_customs_offices(
    db: Session = Depends(get_db),
    actor: User = Depends(require_permission("case.view")),
) -> list[CustomsOffice]:
    return list(db.scalars(select(CustomsOffice).where(CustomsOffice.is_active.is_(True)).order_by(CustomsOffice.name)).all())


@router.post("/case-types", response_model=CaseTypeRead, status_code=status.HTTP_201_CREATED)
def create_case_type(
    payload: CaseTypeCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(require_permission("case_type.manage")),
) -> CaseType:
    case_type = CaseType(**payload.model_dump())
    db.add(case_type)
    db.flush()
    write_audit(db, actor_user_id=actor.id, action="case_type.created", entity_type="case_type", entity_id=str(case_type.id), metadata={"workflow_version": case_type.workflow_version})
    db.commit()
    db.refresh(case_type)
    return case_type


@router.get("/case-types", response_model=list[CaseTypeRead])
def list_case_types(
    db: Session = Depends(get_db),
    actor: User = Depends(require_permission("case.view")),
) -> list[CaseType]:
    return list(db.scalars(select(CaseType).where(CaseType.is_active.is_(True)).order_by(CaseType.name)).all())
