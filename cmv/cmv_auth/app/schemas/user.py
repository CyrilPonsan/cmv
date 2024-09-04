from pydantic import BaseModel, EmailStr, validator

regex_text = r"[\w\sÀ-ÿ«»’',.\-:;!?()–—“”'\"]+"


def escape_special_chars(value):
    value = value.replace("<", "&lt;")
    value = value.replace(">", "&gt;")
    value = value.replace('"', "&quot;")
    return value


class ApiInfos(BaseModel):
    code: str
    token: str


class UserBase(BaseModel):
    username: EmailStr


class UserCreate(UserBase):
    password: str

    @validator("password")
    def check_password(cls, v: str) -> str:
        if len(v) < 8 or len(v) > 50:
            raise ValueError("Password length must be between 8 and 50 characters")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(not c.isalnum() for c in v):
            raise ValueError("Password must contain at least one special character")
        return v


class Role(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class User(UserBase):
    id: int
    role: Role

    class Config:
        from_attributes = True


class AccountInfos(User):
    access_token: str
    refresh_token: str

    class Config:
        from_attributes = True


class RegisterUser(BaseModel):
    user: UserCreate
    role: str


class LoginUser(BaseModel):
    username: str
    password: str
