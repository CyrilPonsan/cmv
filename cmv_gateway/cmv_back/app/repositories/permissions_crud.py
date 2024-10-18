from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from app.sql.models import Permission, Role


# Classe abstraite
class PermissionRead(ABC):
    @abstractmethod
    def read_permission(self, db: Session, role: str, action: str, resource: str):
        pass


# Interface a implémenter par le repository
class PermissionRepository(PermissionRead):
    pass


class PgPermissionRepository(PermissionRepository):
    # Cette méthod retourne une permission pour un rôle, action et ressource donnés
    @staticmethod
    async def check_permission(db: Session, role: str, action: str, resource: str):
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
