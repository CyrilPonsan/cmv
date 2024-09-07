from sqlalchemy.orm import Session

from app.sql.models import Permission


def check_permission(db: Session, role: str, action: str, resource: str):
    return (
        db.query(Permission)
        .filter(
            Permission.role == role,
            Permission.action == action,
            Permission.resource == resource,
        )
        .first()
    )
