from typing import Optional
from pydantic import BaseModel, EmailStr


class UserSchema(BaseModel):
    id: str
    name: str
    email: EmailStr
    password: Optional[str] = None
    role: Optional[int] = 0
    refresh_token: Optional[str] = None
    access_token: Optional[str] = None

    class Config:
        from_attributes = True


class UserSearchingSchema(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: Optional[int] = 0

    class Config:
        from_attributes = True


class UserUpdateSchema(BaseModel):
    name: Optional[str] = None


class SignIn(BaseModel):
    email: EmailStr
    password: str


class SignUp(BaseModel):
    email: EmailStr
    password: str
    name: str
