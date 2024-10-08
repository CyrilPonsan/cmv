from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.sql.models import User


def put_token(db: Session, user_id: int, code: str, token: str):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="L'utilisateur n'existe pas.")

    db_user.code = code
    db_user.token = token
    db_user.updatedAt = datetime.now()

    db.commit()
    db.refresh(db_user)

    print(f"Utilisateur mis à jour : {db_user}")
    return db_user
