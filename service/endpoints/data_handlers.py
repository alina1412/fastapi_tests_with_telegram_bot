import random
import sqlalchemy as sa
from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession

from service.config import key

from service.db_setup.db_settings import get_session
from service.utils import Db
from service.db_setup.models import User


api_router = APIRouter(
    prefix="/v1",
    tags=["private"],
)


@api_router.get(
    "/show",
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Bad request"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Bad request"},
    },
)
async def show_data(
    # user_input: User = Depends(),
    # user_token_data=Depends(get_user_by_token)
):
    """Page"""
    return {"data": key}


@api_router.post(
    "/add",
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Bad request"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Bad request"},
    },
)
async def post_data():
    """"""
    return {"data": "user_token_data"}


@api_router.put(
    "/edit",
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Bad request"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Bad request"},
    },
)
async def put_data2(add_data=None, session: AsyncSession = Depends(get_session)):
    """example with postgres sqlalchemy"""
    add_data = add_data if add_data else str(random.random())
    print(add_data)
    db = Db(User)
    id_ = await db.put(session, {"username": add_data, "password": "bbb"})

    id_ = 0
    conds = (User.id == 103,)
    users = await db.select(session)
    print(users)
    kw = {"id": 100, User.active.key: User.active or 0}
    conds = (
        User.id == kw["id"],
        sa.or_(
            User.active == 1,
            User.password.is_(None),
        ),
    )

    res = await db.update(session, kw, conds)
    id_ = res[0][0] if res and res[0] else None
    try:
        id_ = 3
        await db.delete(session, *(User.id == id_,))
    except Exception as exc:
        id_ = None
        print(exc)
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"No") from exc
    return {"user_id": id_}
