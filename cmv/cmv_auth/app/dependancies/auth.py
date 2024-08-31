from datetime import datetime, timedelta
import secrets

from fastapi import HTTPException, status, Request, Depends
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..crud.auth_crud import check_permission
from ..utils.logging_setup import LoggerSetup


from ..settings.models import User, UserSession
from .db_session import get_db

logger_setup = LoggerSetup()
LOGGER = logger_setup.write_log

# Configuration de l'authentification
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

basic_authorizations = [
    "/api/auth/users/me",
]


# Fonctions d'authentification
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user or not verify_password(password, user.password) or not user.is_active:
        return False
    return user


# Fonction pour créer ou renouveler une session
def create_or_renew_session(db: Session, user_id: int):
    session = db.query(UserSession).filter(UserSession.user_id == user_id).first()
    if session:
        session.expires_at = datetime.now() + timedelta(hours=1)
    else:
        session = UserSession(
            user_id=user_id,
            session_id=secrets.token_urlsafe(32),
            expires_at=datetime.now() + timedelta(hours=1),
        )
        db.add(session)
    db.commit()
    return session.session_id


# Dépendance pour vérifier la session
async def get_current_user(request: Request, db: Session = Depends(get_db)):
    session_id = request.cookies.get("session_id")
    if not session_id:
        print("Get off my lawn!")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="dans le cul lulu"
        )

    session = db.query(UserSession).filter(UserSession.session_id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expirée."
        )
    # Si la session est expirée, elle est supprimée de la db et une exception est levée
    if session.expires_at < datetime.now():
        db.delete(session)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expirée."
        )
    user = db.query(User).filter(User.id == session.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Identifiants incorrects."
        )
    # Renouveler la session
    session.expires_at = datetime.now() + timedelta(hours=1)
    db.add(session)
    db.commit()

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Votre compte n'est pas activé.",
        )
    resource = request.url.path.split("/")[3]
    authorization = check_permission(
        db=db,
        role=user.role.name,
        action=request.method.lower(),
        resource=resource,
    )

    if request.url.path not in basic_authorizations and not authorization:
        LOGGER(
            f"verboten to {request.method.lower()} on {resource} for {user.role.name}",
            request,
        )
        raise HTTPException(
            status_code=403,
            detail="Vous n'êtes pas autorisé à effectuer cette action sur cette ressource.",
        )

    return user
