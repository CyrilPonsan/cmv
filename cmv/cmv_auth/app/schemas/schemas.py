from typing import Optional
from pydantic import BaseModel


class Message(BaseModel):
    message: str


class TokenBase(BaseModel):
    access_token: str
    token_type: str


class RefreshTokenBase(BaseModel):
    refresh_token: str
    token_type: str


class Token(BaseModel):
    id: Optional[int] = None


class RefreshToken(BaseModel):
    id: Optional[int] = None


class Tokens(BaseModel):
    access_token: str
    refresh_token: str
