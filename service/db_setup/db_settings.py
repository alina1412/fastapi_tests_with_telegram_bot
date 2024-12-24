from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from service.config import db_settings


def connect_string() -> str:
    """string without a driver. DB_HOST should be 'db' in docker"""
    return (
        f"{db_settings['db_user']}:{db_settings['db_password']}"
        f"@{db_settings['db_host']}:{db_settings['db_port']}/{db_settings['db_name']}"
    )


def async_database_uri() -> str:
    """Return the async database URL."""
    return "postgresql+asyncpg://" + connect_string()


def sync_database_uri() -> str:
    """Return the sync database URL."""
    return "postgresql://" + connect_string()


class DBManager:
    @property
    def uri(self) -> str:
        return async_database_uri()

    @property
    def engine(self):
        return create_async_engine(self.uri, echo=True, future=True)

    @property
    def session_maker(self):
        return sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )


async def get_session() -> AsyncGenerator:
    async with DBManager().session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception as exc:
            await session.rollback()
            raise exc
        finally:
            await session.close()
