from abc import ABC, abstractmethod

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..sql.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRead(ABC):
    @abstractmethod
    def login(self, db: Session, username: str) -> User:
        pass


class UserRepository(UserRead):
    pass


class PgUserRepository(UserRepository):
    pwd_context = CryptContext

    @staticmethod
    async def get_user(db: Session, username: str) -> User:
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    async def get_user_with_id(db: Session, user_id: int) -> User:
        return db.query(User).filter(User.id_user == user_id).first()
