import pytest
import pytest_asyncio
from typing import Any, Generator

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from service.db_setup.db_settings import DBManager, get_session
from service.__main__ import app


@pytest_asyncio.fixture(name="db", scope="function")
async def get_test_session() -> Generator[sessionmaker, None, None]:
    async with DBManager().session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            await session.close()


@pytest.fixture(name="client", scope="session")
def fixture_client() -> TestClient:  # type: ignore
    with TestClient(app) as client:
        yield client
