import uuid

from pydantic import ConfigDict, EmailStr
from sqlalchemy.dialects.postgresql import TEXT
from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    username: EmailStr
    model_config = ConfigDict(revalidate_instances="always")


class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    username: EmailStr = Field(index=True, unique=True, sa_type=TEXT)
    password_hash: str = Field(nullable=False)


class UserRead(UserBase):
    password: str


class UserCreate(UserBase):
    password: str


class UserPublic(UserBase):
    id: uuid.UUID
    # password_hash: str


class Token(SQLModel):
    token_type: str = "Bearer"
    access_token: str
