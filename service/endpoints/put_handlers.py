import random

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from service.db_setup.db_settings import get_session

api_router = APIRouter(
    prefix="/v1",
    tags=["private"],
)


@api_router.put(
    "/data2",
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Bad request"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Bad request"},
    },
)
async def put_data1(add_data=None, session: AsyncSession = Depends(get_session)):
    """"""
    add_data = add_data if add_data else str(random.random())
    print(add_data)
    return {"user_id": add_data}
