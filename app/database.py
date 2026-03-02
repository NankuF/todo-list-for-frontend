from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.config import PG_DATABASE_URL

DATABASE_URL = PG_DATABASE_URL
async_engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(async_engine, class_=AsyncSession)

async def get_async_db():
    """
    Предоставляет асинхронную сессию SQLAlchemy для работы с базой данных PostgreSQL.
    """
    async with async_session_maker() as session:
        yield session


class Base(DeclarativeBase):
    pass