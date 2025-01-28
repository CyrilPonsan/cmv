# Import des modules nécessaires
from abc import ABC, abstractmethod

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..sql.models import User

# Configuration du contexte de hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRead(ABC):
    """Classe abstraite définissant l'interface de lecture des utilisateurs"""

    @abstractmethod
    def login(self, db: Session, username: str) -> User:
        """Méthode abstraite pour la connexion d'un utilisateur"""
        pass


class UserRepository(UserRead):
    """Classe de base pour le repository des utilisateurs"""

    pass


class PgUserRepository(UserRepository):
    """Implémentation PostgreSQL du repository des utilisateurs"""

    pwd_context = CryptContext

    @staticmethod
    async def get_user(db: Session, username: str) -> User:
        """
        Récupère un utilisateur par son nom d'utilisateur

        Args:
            db (Session): Session de base de données
            username (str): Nom d'utilisateur à rechercher

        Returns:
            User: L'utilisateur trouvé ou None
        """
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    async def get_user_with_id(db: Session, user_id: int) -> User:
        """
        Récupère un utilisateur par son ID

        Args:
            db (Session): Session de base de données
            user_id (int): ID de l'utilisateur à rechercher

        Returns:
            User: L'utilisateur trouvé ou None
        """
        return db.query(User).filter(User.id_user == user_id).first()
