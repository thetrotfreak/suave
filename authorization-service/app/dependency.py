from typing import Annotated, Callable

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from .lifespan import Database


async def get_session():
    """
    FastAPI dependency to yield a session for the sqlalchemy engine

    session is destroyed after request has been serverd
    """
    with Session(Database.engine) as session:
        yield session


DatabaseSession = Annotated[Session, Depends(get_session)]
Authorization = Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())]

AuthorizationHeader: Callable[[HTTPAuthorizationCredentials], dict[str, str]] = (
    lambda obj: {"Authorization": " ".join(obj.model_dump().values())}
)
