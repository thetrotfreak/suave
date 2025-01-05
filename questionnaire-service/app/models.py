from typing import List, Optional

from pydantic import EmailStr
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSON, TEXT
from sqlmodel import Field, SQLModel


class Question(SQLModel):
    text: str
    options: List[str]
    free: bool
    option: Optional[int]


class QuestionnaireBase(SQLModel):
    username: EmailStr = Field(sa_column=Column(TEXT))
    questions: List[Question] = Field(sa_column=Column(JSON))


class Questionnaire(QuestionnaireBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class QuestionnairePublic(QuestionnaireBase):
    id: int


class QuestionnaireCreate(QuestionnaireBase):
    pass


class SurveyResponseBase(SQLModel):
    questionnaire_id: int = Field(foreign_key="questionnaire.id")
    name: str = Field()
    email: EmailStr = Field(index=True)
    answers: List[str] = Field(sa_column=Column(JSON))


class SurveyResponse(SurveyResponseBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class SurveyResponseCreate(SurveyResponseBase):
    pass


class SurveyResponsePublic(SurveyResponseBase):
    id: int
    detail: str = "Your survey has been submitted"
