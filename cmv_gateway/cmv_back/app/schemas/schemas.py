from pydantic import BaseModel


class Message(BaseModel):
    message: str


class Token(BaseModel):
    refresh_token: str
