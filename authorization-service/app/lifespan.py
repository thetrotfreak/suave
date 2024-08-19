from contextlib import asynccontextmanager
from typing import Any, Dict

import redis
from dotenv import dotenv_values, load_dotenv
from fastapi import FastAPI
from sqlalchemy import Engine
from sqlmodel import SQLModel, create_engine

# `create_engine` requires all SQLModel to be avaiable in its metadata
# importing the app.models module puts it into the metadata
from . import models


class Database:
    """
    Calling an instance of `Database` will setup the `SQLModel` Tables

    Provides access to the sqlalchemy engine
    Proivdes access to the synchronous redis instance
    """

    engine: Engine = None
    # TODO use redis.async
    store: redis.Redis = None

    def __init__(self, url: str) -> None:
        Database.url = url

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        Database.engine = create_engine(url=Database.url)
        SQLModel.metadata.create_all(Database.engine)
        Database.store = redis.Redis(decode_responses=True)


class Config:
    """
    Calling an instance of `Config` will load values from .env file

    Provides access to the values via the `Config.env` class attribute

    Raises `EnvironmentError` if any Environment variable failed to load
    """

    env: Dict[str, str | None] = None

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        if not load_dotenv():
            raise EnvironmentError()
        Config.env = dotenv_values()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Authorization Service lifespan

    Set up database engine
    """
    Config()()
    Database(Config.env.get("POSTGRES_URL"))()
    yield
