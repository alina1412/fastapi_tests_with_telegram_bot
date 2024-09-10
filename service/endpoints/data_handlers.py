import random
from typing import Any, Dict, List, Optional, Union
from pydantic import parse_obj_as
from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession

from service.config import key

from service.db_setup.db_settings import get_session
from service.db_watchers import UserDb
from service.schemas import (
    AnswerAddRequest,
    AnswerRequest,
    AnswerSubmitRequest,
    QuestionAddRequest,
    QuestionEditRequest,
    QuestionListRequest,
    QuestionEditRequest,
    QuestionResponse,
    QuizResponse,
)
from service.utils import AnswersManager, QuestionsManager
from service.db_setup.models import Question, User


api_router = APIRouter(
    prefix="/v1",
    tags=["quiz"],
)


@api_router.post(
    "/show-quiz",
    response_model=QuizResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Bad request"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Bad request"},
    },
)
async def show_quiz(
    data: QuestionListRequest, session: AsyncSession = Depends(get_session)
):  # -> list[QuestionResponse]
    """show quiz-test page"""
    q_manager = QuestionsManager(session)
    questions = await q_manager.get_questions_with_answers(data)
    # return QuizResponse.parse_obj(questions)
    return questions if questions else {}


@api_router.post(
    "/questions",
    response_model=list[QuestionResponse],
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Bad request"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Bad request"},
    },
)
async def get_questions(
    data: QuestionListRequest, session: AsyncSession = Depends(get_session)
) -> list[QuestionResponse]:
    """get_questions"""
    q_manager = QuestionsManager(session)
    questions = await q_manager.get_questions(data)
    return questions if questions else []


@api_router.post(
    "/add-question",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Bad request"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Bad request"},
    },
)
async def add_question(
    data: QuestionAddRequest, session: AsyncSession = Depends(get_session)
):
    """request for add-question"""
    q_manager = QuestionsManager(session)
    id_ = await q_manager.add_question(data)
    if id_:
        return {"created": id_}
    return {"not": id_}


@api_router.put(
    "/edit-question",
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Bad request"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Bad request"},
    },
)
async def edit_question(
    params: QuestionEditRequest = Depends(),
    session: AsyncSession = Depends(get_session),
):
    """request for edit_question"""
    q_manager = QuestionsManager(session)
    res = await q_manager.edit_question_by_id(dict(params))
    return {"edited": res}


@api_router.post(
    "/add-answer",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Bad request"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Bad request"},
    },
)
async def add_answer(
    data: AnswerAddRequest, session: AsyncSession = Depends(get_session)
):
    """request for add-answer"""
    a_manager = AnswersManager(session)
    id_ = await a_manager.add_answer(data)
    if id_:
        return {"created": id_}
    raise HTTPException(status.HTTP_400_BAD_REQUEST, f"answer not added")


@api_router.put(
    "/submit-answer",
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Bad request"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Bad request"},
    },
)
async def submit_answer(
    params: AnswerSubmitRequest = Depends(),
    session: AsyncSession = Depends(get_session),
):
    """request for compare_correct_answer"""
    params = dict(params)
    q_manager = QuestionsManager(session)
    res = await q_manager.compare_correct_answer(params)
    if res is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Not found")
    return {"correct": res}


@api_router.put(
    "/edit-user",
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Bad request"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Bad request"},
    },
)
async def user_handler(
    q_id=None, new_data=None, session: AsyncSession = Depends(get_session)
):
    """example with postgres sqlalchemy"""
    add_data = new_data if new_data else str(random.random())
    print(add_data)
    db = UserDb(User)
    id_ = await db.put(session, add_data, "bbb")

    id_ = 0

    users = await db.select_all(session)
    print(users)

    res = await db.update(session)
    id_ = res[0][0] if res and res[0] else None
    try:
        id_ = 3
        await db.delete(session, id_)
    except Exception as exc:
        id_ = None
        print(exc)
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"No") from exc
    return {"user_id": id_}
