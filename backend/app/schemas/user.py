from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    name: str
    
    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()


class UserCreate(UserBase):
    password: str
    role: Optional[str] = "user"
    title: Optional[str] = None
    isAdmin: Optional[bool] = False
    
    @field_validator('password')
    @classmethod
    def password_must_be_strong(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    role: Optional[str] = None
    isActive: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    role: str
    title: Optional[str]
    isAdmin: bool
    isActive: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserSimple(BaseModel):
    id: int
    name: str
    email: str
    role: str
    title: Optional[str]
    isActive: bool

    class Config:
        from_attributes = True


class ChangePassword(BaseModel):
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None
