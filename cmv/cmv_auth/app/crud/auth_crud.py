from sqlalchemy.orm import Session

from ..settings.models import Permission


# retourne la permission si elle existe, dans le cas contraire cela signifie que l'utilisateur ne peut pas effectuer l'action requise sur cette ressource
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
