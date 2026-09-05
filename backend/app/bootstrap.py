from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Permission, Role

SYSTEM_PERMISSIONS = {
    "case.view": "View permitted cases",
    "case.edit": "Edit permitted cases",
    "case.assign": "Assign cases and tasks",
    "case.close": "Close cases",
    "task.create": "Create tasks",
    "task.assign": "Assign tasks",
    "document.upload": "Upload documents",
    "customer_update.publish": "Publish customer-visible updates",
    "customer.manage": "Manage customers and contacts",
    "team.manage": "Manage teams and members",
    "report.view": "View management reports",
    "audit.view": "View security and audit history",
}

SYSTEM_ROLES = {
    "manager": set(SYSTEM_PERMISSIONS),
    "supervisor": {
        "case.view", "case.edit", "case.assign", "case.close", "task.create", "task.assign",
        "document.upload", "customer_update.publish", "customer.manage", "report.view",
    },
    "employee": {
        "case.view", "case.edit", "task.create", "task.assign", "document.upload", "customer_update.publish",
    },
    "customer": {"case.view", "document.upload"},
}


def seed_access_control(db: Session) -> None:
    permission_by_code: dict[str, Permission] = {}
    for code, description in SYSTEM_PERMISSIONS.items():
        permission = db.scalar(select(Permission).where(Permission.code == code))
        if permission is None:
            permission = Permission(code=code, description=description)
            db.add(permission)
            db.flush()
        permission_by_code[code] = permission

    for role_code, permission_codes in SYSTEM_ROLES.items():
        role = db.scalar(select(Role).where(Role.code == role_code))
        if role is None:
            role = Role(code=role_code, name=role_code.replace("_", " ").title(), is_system=True)
            db.add(role)
            db.flush()
        role.permissions = [permission_by_code[code] for code in sorted(permission_codes)]

    db.commit()
