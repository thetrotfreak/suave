import uuid

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    username: EmailStr


class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    username: str = Field(index=True, unique=True)
    password_hash: str = Field(nullable=False)


class UserRead(UserBase):
    password: str


class UserCreate(UserBase):
    password: str


class UserPublic(UserBase):
    id: uuid.UUID
    password_hash: str


class Token(SQLModel):
    token_type: str = "Bearer"
    access_token: str
