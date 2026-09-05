import json
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.models import AuditLog


def write_audit(
    db: Session,
    *,
    actor_user_id: UUID | None,
    action: str,
    entity_type: str,
    entity_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    db.add(
        AuditLog(
            actor_user_id=actor_user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata_json=json.dumps(metadata, ensure_ascii=False, default=str) if metadata else None,
        )
    )
