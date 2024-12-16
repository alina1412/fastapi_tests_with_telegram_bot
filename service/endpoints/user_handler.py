import random

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from service.config import logger
from service.db_setup.db_settings import get_session
from service.db_watchers import UserDb
from service.db_setup.models import User

api_router = APIRouter(
    prefix="/v1",
    tags=["private"],
)


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
    """Example with postgres sqlalchemy"""
    add_data = new_data if new_data else str(random.random())
    logger.info(add_data)
    db = UserDb(User)
    id_ = await db.put(session, add_data, "bbb")

    id_ = 0

    users = await db.select_all(session)
    logger.info(users)

    res = await db.update(session)
    id_ = res[0][0] if res and res[0] else None
    try:
        id_ = 3
        await db.delete(session, id_)
    except Exception as exc:
        id_ = None
        logger.error("error", exc_info=exc)
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No") from exc
    return {"user_id": id_}
