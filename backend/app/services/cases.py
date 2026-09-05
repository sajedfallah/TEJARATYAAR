from datetime import datetime, timezone
from uuid import UUID

import jdatetime
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.operational_models import Case, CaseSequence, CaseStatus, CaseType, CustomsOffice, PreCase
from app.services.audit import write_audit


def current_jalali_year() -> int:
    return jdatetime.date.today().year


def next_case_number(db: Session) -> str:
    year = current_jalali_year()
    sequence = db.scalar(select(CaseSequence).where(CaseSequence.jalali_year == year).with_for_update())
    if sequence is None:
        sequence = CaseSequence(jalali_year=year, last_value=0)
        db.add(sequence)
        db.flush()
    sequence.last_value += 1
    return f"{year}-{sequence.last_value:04d}"


def create_pre_case(
    db: Session,
    *,
    customer_id: UUID,
    case_type_id: UUID,
    customs_office_id: UUID,
    created_by_id: UUID,
    team_id: UUID | None = None,
    source_request_id: UUID | None = None,
) -> PreCase:
    case_type = db.get(CaseType, case_type_id)
    customs = db.get(CustomsOffice, customs_office_id)
    if case_type is None or not case_type.is_active:
        raise ValueError("Case type is not active")
    if customs is None or not customs.is_active:
        raise ValueError("Customs office is not active")

    resolved_team_id = team_id or customs.default_team_id
    pre_case = PreCase(
        customer_id=customer_id,
        case_type_id=case_type_id,
        customs_office_id=customs_office_id,
        team_id=resolved_team_id,
        created_by_id=created_by_id,
        source_request_id=source_request_id,
    )
    db.add(pre_case)
    db.flush()
    write_audit(
        db,
        actor_user_id=created_by_id,
        action="pre_case.created",
        entity_type="pre_case",
        entity_id=str(pre_case.id),
        metadata={"customer_id": customer_id, "case_type_id": case_type_id, "customs_office_id": customs_office_id},
    )
    return pre_case


def activate_pre_case(
    db: Session,
    *,
    pre_case_id: UUID,
    customs_declaration_number: str,
    actor_user_id: UUID,
) -> Case:
    pre_case = db.scalar(select(PreCase).where(PreCase.id == pre_case_id).with_for_update())
    if pre_case is None:
        raise ValueError("Pre-case not found")
    if pre_case.converted_case_id is not None:
        case = db.get(Case, pre_case.converted_case_id)
        if case is None:
            raise RuntimeError("Pre-case conversion state is inconsistent")
        return case

    duplicate = db.scalar(select(Case).where(Case.customs_declaration_number == customs_declaration_number))
    if duplicate is not None:
        raise ValueError(f"Customs declaration number already belongs to case {duplicate.case_number}")

    case_type = db.get(CaseType, pre_case.case_type_id)
    if case_type is None:
        raise RuntimeError("Case type is missing")

    case = Case(
        case_number=next_case_number(db),
        customs_declaration_number=customs_declaration_number.strip(),
        customer_id=pre_case.customer_id,
        case_type_id=pre_case.case_type_id,
        workflow_version=case_type.workflow_version,
        customs_office_id=pre_case.customs_office_id,
        team_id=pre_case.team_id,
        status=CaseStatus.ACTIVE,
    )
    db.add(case)
    db.flush()

    pre_case.converted_case_id = case.id
    pre_case.converted_at = datetime.now(timezone.utc)
    write_audit(
        db,
        actor_user_id=actor_user_id,
        action="case.activated",
        entity_type="case",
        entity_id=str(case.id),
        metadata={"case_number": case.case_number, "customs_declaration_number": case.customs_declaration_number, "pre_case_id": pre_case.id},
    )

    try:
        db.flush()
    except IntegrityError as exc:
        raise ValueError("Case number or customs declaration number already exists") from exc
    return case
