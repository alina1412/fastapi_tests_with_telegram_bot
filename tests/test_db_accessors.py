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
async def test_db_add_remove_question(db):
    q_manager = QuestionDb(db)

    data = InputData(active=1, limit=50, offset=0, order="updated_dt", text="question")
    id_ = await q_manager.add_question(data.model_dump(include={"active", "text"}))
    print("-------")
    print(id_)
    print("-------")
    logger.info(id_)

    res = await q_manager.remove_question(id_)
    logger.info(res)
    assert res


@pytest.mark.asyncio
async def test_db_get_question(db):
    q_manager = QuestionDb(db)
    data = InputData(active=1, limit=50, offset=0, order="id", text="question")
    questions = await q_manager.get_questions(data)
    print("-------")
    list_ids = [question.id for question in questions]
    print(list_ids)
    print("-------")
    logger.info(questions)
