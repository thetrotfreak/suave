from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import Session, create_engine

from app.models import Questionnaire, SQLModel, SurveyResponse

# Check this link for the "why unused imports?"
# https://sqlmodel.tiangolo.com/tutorial/create-db-and-table/#sqlmodel-metadata-order-matters


engine = create_engine(url="postgresql://user:password@db:5432/survey_db", echo=True)


def get_session():
    """
    Create a session to work with the database engine
    """
    with Session(engine) as session:
        yield session


@asynccontextmanager
async def create_db_and_relation(app: FastAPI):
    """
    FastAPI lifecycle

    Create required database tables
    """

    SQLModel.metadata.create_all(engine)
    # setup
    yield
    # teardown
    pass
