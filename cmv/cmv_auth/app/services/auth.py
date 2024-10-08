from fastapi import HTTPException, Request, status
from sqlalchemy.orm import Session

from app.repositories.user_crud import UserRepository


class AuthService:
    credentials_arror = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identifiant ou mot de passe incorrect. Dans le cul lulu !",
    )

    def __init__(self, repository: UserRepository):
        pass

    async def login(db: Session, request: Request, username: str, password: str):
        pass
