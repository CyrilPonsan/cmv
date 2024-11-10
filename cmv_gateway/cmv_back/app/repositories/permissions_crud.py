from sqlalchemy.orm import Session

from app.sql.models import Permission, Role


# Repository des permissions
class PermissionRepository:
    @staticmethod
    async def check_permission(
        db: Session, role: str, action: str, resource: str
    ) -> bool:
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
