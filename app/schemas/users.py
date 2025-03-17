import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, constr

from app.core.config import AccountStatuses, Roles


class UserSchema(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: Optional[str] = Roles.USER.value
    phone: Optional[str] = None
    address: Optional[str] = None
    dob: Optional[datetime.datetime] = None  # type: ignore
    create_at: Optional[datetime.datetime] = None  # type: ignore
    update_at: Optional[datetime.datetime] = None  # type: ignore

    class Config:
        from_attributes = True


class TokenPair(BaseModel):
    refresh_token: Optional[str] = None
    access_token: Optional[str] = None

    class Config:
        from_attributes = True


class UserSearchingSchema(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: Optional[str] = Roles.USER.value
    phone: Optional[str] = None
    address: Optional[str] = None
    dob: Optional[datetime.datetime] = None
    status: Optional[str] = AccountStatuses.ACTIVE.value

    class Config:
        from_attributes = True


class UserUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100, example="John Doe")
    phone: Optional[str] = Field(
        None,
        pattern=r"^\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$",
        example="0412345678",
    )
    address: Optional[str] = Field(None, max_length=255, example="123 Street, City")
    dob: Optional[datetime.datetime] = Field(None, example="1990-01-01T00:00:00")

    class Config:
        from_attributes = True


class SignIn(BaseModel):
    email: EmailStr
    password: str


class SignUp(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone: str = Field(
        pattern=r"^\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$",
        example="0412345678",
    )
    address: Optional[str] = None
    dob: Optional[datetime.datetime] = None  # type: ignore
