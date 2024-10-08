from sqlalchemy.orm import Session

from app.sql.models import Permission, Role


def check_permission(db: Session, role: str, action: str, resource: str):
    return (
        db.query(Permission)
        .join(Role)
        .filter(
            Role.name == role,
            Permission.action == action,
            Permission.resource == resource,
        )
        .first()
    )
