from fastapi import Depends
import pytest_asyncio
import asyncio
import pytest
import logging
from pydantic import BaseModel

from service.db_watchers import AnswerDb, QuestionDb
from service.schemas import QuestionListRequest
from service.utils import QuestionsManager
from service.db_setup.models import Answer, Question, User, Base
from tests.conftest import get_test_session


pytest_plugins = ("pytest_asyncio",)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class InputData(BaseModel):
    active: int
    limit: int
    offset: int
    order: str
    text: str


@pytest.mark.asyncio
async def test_show_questions_handler(db, client):
    url = "/v1/questions"
    input_data = {
        "active": 1,
        "limit": 50,
        "offset": 0,
        "order": "updated_dt",
        "text": "question",
    }
    response = client.post(url, json=input_data)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_db(db):
    q_manager = QuestionDb(db)

    data = InputData(active=1, limit=50, offset=0, order="updated_dt", text="question")
    res = await q_manager.add_question(data.model_dump(include={"active", "text"}))
    print("-------")
    print(res)
    print("-------")
    # logger.info(res)

    questions = await q_manager.get_questions(data)
    print("-------")
    print([question.id for question in questions])
    print("-------")
    # logger.info(questions)
