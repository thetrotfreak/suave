import uuid

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: uuid.UUID = Field(
        default=uuid.uuid4, primary_key=True, index=True, nullable=False
    )
    email: EmailStr = Field(index=True, unique=True, nullable=False)
    password_hash: bytes = Field(nullable=False)
    salt: bytes = Field(nullable=False)
