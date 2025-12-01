from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.auth import AuthRequest
from app.auth.jwt import verify_password


async def authenticate_user(db: AsyncSession, auth_data: AuthRequest) -> bool:
    """Аутентифицирует пользователя (для обратной совместимости)"""
    result = await db.execute(select(User).where(User.name == auth_data.name))
    user = result.scalar_one_or_none()
    
    if not user:
        return False
    
    return verify_password(auth_data.password, user.password)
