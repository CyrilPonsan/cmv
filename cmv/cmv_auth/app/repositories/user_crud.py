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


class PostgresAuthRepository(UserRepository):
    pwd_context = CryptContext

    @staticmethod
    async def get_user(db: Session, username: str) -> User:
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    async def get_user_with_id(db: Session, user_id: int) -> User:
        return db.query(User).filter(User.id_user == user_id).first()


"""
# retourne un utilisateur grâce à son identifiant
def get_user_with_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


# retourne un utilisateur d'après son identifiant
def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, data: RegisterUser):
    user = data.user
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un compte avec cette adresse exise déjà",
        )
    existing_role = db.query(Role).filter(Role.name == data.role).first()
    if not existing_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Le rôle n'existe pas."
        )

    hashed_password = pwd_context.hash(user.password)
    new_user = User(
        username=user.username,
        password=hashed_password,
        role=existing_role,
        first_name=user.first_name,
        last_name=user.last_name,
        service=data.role,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user.id


def get_offset(page: int, limit: int):
    return limit * page


def get_all_users(db: Session):
    print("not from cache")
    result = db.query(User).all()

    users = []

    for r in result:
        user = {"id": r.id, "username": r.username, "role": r.role.name}
        users.append(user)
    return users
"""
