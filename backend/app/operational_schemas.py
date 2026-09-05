from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models import CustomerType
from app.operational_models import CasePriority, CaseStatus, ConfidentialityLevel


class CustomerCreate(BaseModel):
    customer_type: CustomerType
    name: str = Field(min_length=2, max_length=180)
    trade_name: str | None = Field(default=None, max_length=180)
    phone: str | None = Field(default=None, max_length=40)
    address: str | None = None


class CustomerRead(CustomerCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    is_active: bool


class ContactCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    role_title: str | None = Field(default=None, max_length=120)
    phone: str | None = Field(default=None, max_length=40)
    can_create_request: bool = False
    is_primary: bool = False


class ContactRead(ContactCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    customer_id: UUID
    telegram_id: int | None
    is_active: bool


class TeamCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    supervisor_id: UUID | None = None


class TeamRead(TeamCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    is_active: bool


class CustomsOfficeCreate(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    code: str | None = Field(default=None, max_length=60)
    default_team_id: UUID | None = None
    default_supervisor_id: UUID | None = None


class CustomsOfficeRead(CustomsOfficeCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    is_active: bool


class CaseTypeCreate(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    code: str = Field(min_length=2, max_length=80, pattern=r"^[a-z0-9_-]+$")
    description: str | None = None


class CaseTypeRead(CaseTypeCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    workflow_version: int
    is_active: bool


class PreCaseCreate(BaseModel):
    customer_id: UUID
    case_type_id: UUID
    customs_office_id: UUID
    team_id: UUID | None = None
    source_request_id: UUID | None = None


class PreCaseRead(PreCaseCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    created_by_id: UUID
    converted_case_id: UUID | None
    converted_at: datetime | None
    created_at: datetime


class ActivatePreCaseRequest(BaseModel):
    customs_declaration_number: str = Field(min_length=2, max_length=80)


class CaseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    case_number: str
    customs_declaration_number: str
    customer_id: UUID
    case_type_id: UUID
    workflow_version: int
    customs_office_id: UUID
    team_id: UUID | None
    primary_owner_id: UUID | None
    status: CaseStatus
    customer_status: str
    priority: CasePriority
    confidentiality: ConfidentialityLevel
    bill_of_lading_number: str | None
    warehouse_receipt_number: str | None
    carrier_name: str | None
    next_action_title: str | None
    next_action_owner_id: UUID | None
    next_action_due_at: datetime | None
    opened_at: datetime


class InviteCreate(BaseModel):
    role_code: str = Field(min_length=2, max_length=80)
    customer_id: UUID | None = None
    contact_id: UUID | None = None
    expires_in_hours: int = Field(default=72, ge=1, le=720)


class InviteCreated(BaseModel):
    id: UUID
    token: str
    expires_at: datetime


class InviteActivate(BaseModel):
    token: str = Field(min_length=20)
    init_data: str = Field(min_length=1)


class UserListItem(BaseModel):
    id: UUID
    telegram_id: int | None
    first_name: str
    last_name: str | None
    username: str | None
    status: str
    roles: list[str]
