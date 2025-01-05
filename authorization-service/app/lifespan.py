from contextlib import asynccontextmanager
from typing import Any, Dict, Generator, Annotated

from redis import Redis
from dotenv import dotenv_values, load_dotenv
from fastapi import FastAPI
from sqlalchemy import Engine
from sqlmodel import SQLModel, create_engine
from starlette.datastructures import State
from joserfc.jwk import OctKey

# `create_engine` requires all SQLModel to be avaiable in its metadata
# importing the app.models module puts it into the metadata
from . import models


class Database:
    """
    Calling an instance of `Database` will setup the `SQLModel` Tables

    Provides access to the sqlalchemy engine
    Proivdes access to the synchronous redis instance
    """

    engine: Engine
    # TODO use redis.async
    cache: Redis

    def __init__(self, url: str) -> None:
        Database.url = url

    # def __call__(self, *args: Any, **kwds: Any) -> Generator[State, None, None]:
    def __call__(self, *args: Any, **kwds: Any):
        Database.engine = create_engine(url=Database.url)
        SQLModel.metadata.create_all(Database.engine)
        Database.cache = Redis(host="redis", port=6379, decode_responses=True)
        # yield
        # yield State(state=Database.store)
        # with Redis(decode_responses=True) as r:
        #     yield State(state={})
        # Database.store.close()


class Config:
    """
    Calling an instance of `Config` will load values from .env file

    Provides access to the values via the `Config.env` class attribute

    Raises `EnvironmentError` if any Environment variable failed to load
    """

    env: Dict[str, str | int | OctKey | None]

    def __call__(self, *args: Any, **kwds: Any):
        if not load_dotenv():
            raise EnvironmentError()
        Config.env = dotenv_values()
        Config.env.update(
            {
                "ACCESS_TOKEN_EXPIRE_MINUTES": int(
                    Config.env.get("ACCESS_TOKEN_EXPIRE_MINUTES")
                ),
                "SECRET_KEY": OctKey.import_key(value=Config.env.get("SECRET_KEY")),
            }
        )
        for k, v in Config.env.items():
            setattr(Config, k, v)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Authorization Service lifespan

    Set up database engine
    """
    Config()()
    Database(url=Config.POSTGRES_URL)()
    yield
