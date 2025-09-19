from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker

from service.config import db_settings


def connect_string() -> str:
    """String without a driver. DB_HOST should be 'db' in docker."""
    return (
        f"{db_settings['db_user']}:{db_settings['db_password']}"
        f"@{db_settings['db_host']}:{db_settings['db_port']}/{db_settings['db_name']}"
    )


def async_database_uri() -> str:
    """Return the async database URL."""
    return db_settings["db_driver"] + "://" + connect_string()


class DBManager:
    def __init__(self):
        self.engine = None

    @property
    def uri(self) -> str:
        return async_database_uri()

    def get_engine(self):
        self.engine = create_async_engine(
            self.uri,
            pool_size=1,
            max_overflow=0,
            pool_recycle=280,
            pool_timeout=20,
            echo=True,
            future=True,
        )
        return self.engine

    @property
    def session_maker(self):
        if not self.engine:
            self.get_engine()
        return sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )


async def get_session() -> AsyncGenerator:
    db_manager = DBManager()
    async with db_manager.session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception as exc:
            await session.rollback()
            raise exc
        finally:
            await session.close()
            if db_manager.engine:
                await db_manager.engine.dispose()
