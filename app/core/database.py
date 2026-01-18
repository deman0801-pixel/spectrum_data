from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
    
)

from app.core.config import settings

USER = settings.POSTGRES_USER
PASSWORD = settings.POSTGRES_PASSWORD
HOST = settings.POSTGRES_HOST
PORT = settings.POSTGRES_PORT
DB = settings.POSTGRES_DB

async_database_url = f"postgresql+asyncpg://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}"

engine: AsyncEngine = create_async_engine(
    async_database_url,
    echo=False,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=40,
    pool_recycle=3600,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def get_db_connection() -> AsyncGenerator[AsyncConnection, None]:
    connection = None
    try:
        connection = await engine.connect()
        yield connection
    finally:
        if connection:
            await connection.close()