# Import des modules nécessaires de SQLAlchemy
from sqlalchemy.orm import Session

# Import des modèles de données
from app.sql.models import Permission, Role


# Repository des permissions pour gérer les accès
class PermissionRepository:
    @staticmethod
    async def check_permission(
        db: Session, role: str, action: str, resource: str
    ) -> bool:
        """
        Vérifie si un rôle a la permission d'effectuer une action sur une ressource.

        Args:
            db (Session): Session de base de données SQLAlchemy
            role (str): Nom du rôle à vérifier
            action (str): Action à vérifier (ex: 'read', 'write', etc.)
            resource (str): Ressource sur laquelle l'action est effectuée

        Returns:
            bool: True si la permission existe, False sinon
        """
        return (
            # Création de la requête sur la table Permission
            db.query(Permission)
            # Jointure avec la table Role
            .join(Role)
            # Filtrage selon les critères fournis
            .filter(
                Role.name == role,  # Vérifie le nom du rôle
                Permission.action == action,  # Vérifie l'action
                Permission.resource == resource,  # Vérifie la ressource
            )
            # Récupère le premier résultat trouvé
            .first()
        )
