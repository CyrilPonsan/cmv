from pydantic import BaseModel


class SuccessWithMessage(BaseModel):
    success: bool
    message: str
