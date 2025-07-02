from app.config import settings

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.exc import DBAPIError

engine = create_async_engine(
    settings.database_url,
)

async_session_maker = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False
)


async def get_session():
    async with async_session_maker() as session:
        try:
            yield session
        except DBAPIError:
            await session.rollback()
            raise
        finally:
            await session.close()
