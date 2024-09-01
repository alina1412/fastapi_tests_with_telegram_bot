import random
import sqlalchemy as sa
from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession

from service.config import key

from service.db_setup.db_settings import get_session
from service.db_watchers import UserDb
from service.utils import QuestionsManager, AnswersManager
from service.db_setup.models import User


api_router = APIRouter(
    prefix="/v1",
    tags=["private"],
)


@api_router.get(
    "/show-quiz",
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Bad request"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Bad request"},
    },
)
async def show_quiz(user_id=1, session: AsyncSession = Depends(get_session)):
    """show quiz-test page"""
    q_manager = QuestionsManager(session)
    id_ = 1
    q = q_manager.get_question(id_)
    questions = q_manager.get_all_questions()
    return {"data": questions}


@api_router.post(
    "/add-question",
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Bad request"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Bad request"},
    },
)
async def add_question(session: AsyncSession = Depends(get_session)):
    """request for add-question"""
    q_manager = QuestionsManager(session)
    id_ = 1
    # return {"id": id_}
    return {"TODO": "TODO"}


@api_router.put(
    "/edit-question",
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Bad request"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Bad request"},
    },
)
async def edit_question(
    q_id=None, new_text=None, session: AsyncSession = Depends(get_session)
):
    """request for edit_question"""

    return {"TODO": "TODO"}


@api_router.put(
    "/edit-user",
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Bad request"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Bad request"},
    },
)
async def user_handler(
    q_id=None, new_text=None, session: AsyncSession = Depends(get_session)
):
    """example with postgres sqlalchemy"""
    add_data = add_data if add_data else str(random.random())
    print(add_data)
    db = UserDb(User)
    id_ = await db.put(session, add_data, "bbb")

    id_ = 0
    # conds = (User.id == 103,)
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
