from datetime import datetime, timedelta, timezone
import secrets

from fastapi import HTTPException, status, Request, Depends
from passlib.context import CryptContext
from sqlalchemy.orm import Session


from ..models import User, UserSession
from .db_session import get_db

# Configuration de l'authentification
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Fonctions d'authentification
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user


# Fonction pour créer ou renouveler une session
def create_or_renew_session(db: Session, user_id: int):
    session = db.query(UserSession).filter(UserSession.user_id == user_id).first()
    if session:
        session.expires_at = datetime.utcnow() + timedelta(days=1)
    else:
        session = UserSession(
            user_id=user_id,
            session_id=secrets.token_urlsafe(32),
            expires_at=datetime.utcnow() + timedelta(days=1)
        )
        db.add(session)
    db.commit()
    return session.session_id


# Dépendance pour vérifier la session
async def get_current_user(request: Request, db: Session = Depends(get_db)):
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated")

    session = db.query(UserSession).filter(UserSession.session_id == session_id).first()
    if not session or session.expires_at < datetime.now():
        raise HTTPException(status_code=401, detail="Session expired")

    user = db.query(User).filter(User.id == session.user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # Renouveler la session
    session.expires_at = datetime.now() + timedelta(days=1)
    db.commit()

    return user
