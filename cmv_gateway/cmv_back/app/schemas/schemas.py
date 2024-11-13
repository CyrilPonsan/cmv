from pydantic import BaseModel


class Message(BaseModel):
    message: str


class SuccessWithMessage(BaseModel):
    success: bool
    message: str
