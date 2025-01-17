from sqlalchemy.orm import Session

from app.crud.user import put_token


def update_user(db: Session, user_id: int, code: str, token: str):
    return put_token(db, user_id, code, token)
