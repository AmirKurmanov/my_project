from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class DatabaseManager:
    def __init__(self, db_url: str):
        self.__db_url = db_url
        self.__engine = None
        self.__session_maker = None

    async def __aenter__(self):
        self.__engine = create_async_engine(self.__db_url, echo=True)
        self.__session_maker = async_sessionmaker(
            self.__engine, class_=AsyncSession, autoflush=False, expire_on_commit=False
        )

        async with self.__engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.__engine:
            await self.__engine.dispose()

    @asynccontextmanager
    async def get_session(self):
        if self.__session_maker is None:
            raise RuntimeError("Database not initialized. Use 'async with' block.")
        
        async with self.__session_maker() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

# Глобальная функция для получения сессии
async def get_db():
    from coffee_shop.main import db_manager
    async with db_manager.get_session() as session:
        yield session