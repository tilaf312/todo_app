from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate
from app.auth.jwt import get_password_hash
from fastapi import HTTPException, status


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    """Создает нового пользователя"""
    # Проверяем, существует ли пользователь
    result = await db.execute(select(User).where(User.name == user.name))
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже существует"
        )

    hashed_password = get_password_hash(user.password)
    db_user = User(name=user.name, password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_user_by_name(db: AsyncSession, name: str) -> User | None:
    """Получает пользователя по имени"""
    result = await db.execute(select(User).where(User.name == name))
    return result.scalar_one_or_none()
