import uuid

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(index=True)
    password_hash: str
    salt: str


class SignInRequest(SQLModel):
    email: EmailStr
    password_hash: str
