from fastapi import Depends, FastAPI, HTTPException, status
from sqlmodel import Session

from app.database import create_db_and_relation, get_session
from app.models import (
    Questionnaire,
    QuestionnaireCreate,
    QuestionnairePublic,
    SurveyResponse,
    SurveyResponseCreate,
    SurveyResponsePublic,
)

app = FastAPI(
    title="Suave Survey Questionnaire API",
    summary="Participate in a questionnare based survey",
    version="0.1.0",
    lifespan=create_db_and_relation,
)


@app.post("/api/questionnaire/v1", response_model=QuestionnairePublic)
def create_questionnaire(
    questionnaire: QuestionnaireCreate, session: Session = Depends(get_session)
):
    if len(questionnaire.questions) < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The questionnaire must have at least 1 question",
        )

    questionnaire = Questionnaire(questions=questionnaire.questions)
    session.add(questionnaire)
    session.commit()
    session.refresh(questionnaire)
    return questionnaire


@app.get("/questionnaire/{questionnaire_id}", response_model=QuestionnairePublic)
def get_questionnaire(questionnaire_id: int, session: Session = Depends(get_session)):
    questionnaire = session.get(Questionnaire, questionnaire_id)
    if not questionnaire:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Questionnaire not found"
        )
    return questionnaire


@app.post("/survey/{questionnaire_id}", response_model=SurveyResponsePublic)
def submit_survey(
    questionnaire_id: int,
    response: SurveyResponseCreate,
    session: Session = Depends(get_session),
):
    questionnaire = session.get(Questionnaire, questionnaire_id)
    if not questionnaire:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Questionnaire not found"
        )

    if len(response.answers) < len(questionnaire.questions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing answers to some questions",
        )

    survey_response = SurveyResponse(
        name=response.name,
        email=response.email,
        questionnaire_id=response.questionnaire_id,
        answers=response.answers,
    )
    session.add(survey_response)
    session.commit()
    session.refresh(survey_response)
    return survey_response
