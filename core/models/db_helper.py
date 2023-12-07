from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

from core.config import DATABASE_URL


class DatabaseHelper:
    def __init__(self, url: str, echo: bool = False):
        self.engine = create_async_engine(url=url, echo=echo)
        self.session = async_sessionmaker(
            bind=self.engine, autoflush=False, autocommit=False, expire_on_commit=False
        )

    async def session_dependency(self) -> AsyncSession:
        async with self.session as ses:
            yield ses
            ses.close()


db_helper = DatabaseHelper(url=DATABASE_URL, echo=False)
