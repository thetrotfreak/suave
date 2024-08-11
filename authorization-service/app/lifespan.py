from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel, create_engine

# `create_engine` requires all SQLModel to be avaiable in its metadata
# importing the app.models module put it into the metadata
from . import models


@asynccontextmanager
async def lifespan_setup_database(app: FastAPI):
    """
    Authorization Service lifespan

    Set up database engine
    """
    sqlite_file_name = "database.db"
    sqlite_url = f"sqlite:///{sqlite_file_name}"

    engine = create_engine(url=sqlite_url)
    SQLModel.metadata.create_all(engine)
    yield
