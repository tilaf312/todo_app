from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool
from typing import AsyncGenerator

from app.config import settings


class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass


# Создаем async engine
# Для SQLite используем NullPool для лучшей совместимости с async
if settings.DATABASE_URL and settings.DATABASE_URL.startswith("sqlite"):
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DB_ECHO,
        poolclass=NullPool,
        connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
    )
else:
    # Для PostgreSQL и других БД используем обычный пул
    engine = create_async_engine(
        settings.DATABASE_URL or "postgresql+asyncpg://todo_user:vfrcbv@localhost:5432/todo_db",
        echo=settings.DB_ECHO,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
    )


# Создаем фабрику async сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для получения async сессии базы данных.
    
    Yields:
        AsyncSession: Сессия базы данных
        
    Example:
        ```python
        async def my_endpoint(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User))
            return result.scalars().all()
        ```
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Инициализирует базу данных - создает все таблицы.
    
    Вызывается при старте приложения.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    Закрывает соединения с базой данных.
    
    Вызывается при остановке приложения.
    """
    await engine.dispose()
