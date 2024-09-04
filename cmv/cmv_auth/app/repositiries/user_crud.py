from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status

from ..settings import models
from ..schemas.user import RegisterUser

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# retourne un utilisateur grâce à son identifiant
def get_user_by_id(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    return user


# username est le nom donné au champ email dans la bdd
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, data: RegisterUser):
    user = data.user
    existing_user = (
        db.query(models.User).filter(models.User.username == user.username).first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un compte avec cette adresse exise déjà",
        )
    existing_role = db.query(models.Role).filter(models.Role.name == data.role).first()
    if not existing_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Le rôle n'existe pas."
        )

    hashed_password = pwd_context.hash(user.password)
    new_user = models.User(
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
    result = db.query(models.User).all()

    users = []

    for r in result:
        user = {"id": r.id, "username": r.username, "role": r.role.name}
        users.append(user)
    return users
