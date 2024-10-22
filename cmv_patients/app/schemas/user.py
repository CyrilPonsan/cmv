from datetime import datetime

from pydantic import BaseModel


class InternalPayload(BaseModel):
    user_id: int
    role: str
    exp: datetime
    source: str
