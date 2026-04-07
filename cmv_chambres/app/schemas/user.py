from datetime import datetime

from pydantic import BaseModel


class InternalPayload(BaseModel):
    # Identifiant unique de l'utilisateur
    user_id: int
    # Rôle de l'utilisateur (ex: admin, user, etc.)
    role: str
    # Date d'expiration du token
    exp: datetime
    # Source de la requête (ex: web, mobile, etc.)
    source: str
