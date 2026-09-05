import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CaseStatus(str, enum.Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class CasePriority(str, enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class ConfidentialityLevel(str, enum.Enum):
    NORMAL = "normal"
    RESTRICTED = "restricted"
    MANAGER_ONLY = "manager_only"


class CustomerUserLink(Base):
    __tablename__ = "customer_user_links"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), primary_key=True)
    contact_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("customer_contacts.id", ondelete="SET NULL"), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class CustomsOffice(Base):
    __tablename__ = "customs_offices"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    code: Mapped[str | None] = mapped_column(String(60), unique=True)
    default_team_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("teams.id", ondelete="SET NULL"))
    default_supervisor_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class CaseType(Base):
    __tablename__ = "case_types"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    code: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    workflow_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class PreCase(Base):
    __tablename__ = "pre_cases"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="RESTRICT"), index=True)
    case_type_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("case_types.id", ondelete="RESTRICT"), index=True)
    customs_office_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("customs_offices.id", ondelete="RESTRICT"), index=True)
    team_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("teams.id", ondelete="SET NULL"), index=True)
    created_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"))
    source_request_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    converted_case_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), unique=True)
    converted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class CaseSequence(Base):
    __tablename__ = "case_sequences"

    jalali_year: Mapped[int] = mapped_column(Integer, primary_key=True)
    last_value: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class Case(Base):
    __tablename__ = "cases"
    __table_args__ = (
        UniqueConstraint("case_number", name="uq_cases_case_number"),
        UniqueConstraint("customs_declaration_number", name="uq_cases_customs_declaration_number"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_number: Mapped[str] = mapped_column(String(24), index=True)
    customs_declaration_number: Mapped[str] = mapped_column(String(80), index=True)
    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="RESTRICT"), index=True)
    case_type_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("case_types.id", ondelete="RESTRICT"), index=True)
    workflow_version: Mapped[int] = mapped_column(Integer, nullable=False)
    customs_office_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("customs_offices.id", ondelete="RESTRICT"), index=True)
    team_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("teams.id", ondelete="SET NULL"), index=True)
    primary_owner_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), index=True)
    status: Mapped[CaseStatus] = mapped_column(Enum(CaseStatus, name="case_status"), default=CaseStatus.ACTIVE, nullable=False, index=True)
    customer_status: Mapped[str] = mapped_column(String(120), default="در حال انجام", nullable=False)
    priority: Mapped[CasePriority] = mapped_column(Enum(CasePriority, name="case_priority"), default=CasePriority.NORMAL, nullable=False)
    confidentiality: Mapped[ConfidentialityLevel] = mapped_column(Enum(ConfidentialityLevel, name="confidentiality_level"), default=ConfidentialityLevel.NORMAL, nullable=False)
    bill_of_lading_number: Mapped[str | None] = mapped_column(String(120), index=True)
    warehouse_receipt_number: Mapped[str | None] = mapped_column(String(120), index=True)
    warehouse_receipt_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    carrier_name: Mapped[str | None] = mapped_column(String(180))
    next_action_title: Mapped[str | None] = mapped_column(String(255))
    next_action_owner_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    next_action_due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class CaseContactAccess(Base):
    __tablename__ = "case_contact_access"

    case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), primary_key=True)
    contact_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("customer_contacts.id", ondelete="CASCADE"), primary_key=True)
    can_create_request: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
