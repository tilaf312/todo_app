from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.models.user import User
from app.database import get_db
from app.config import settings

# Настройки безопасности
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет пароль против хеша"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Хеширует пароль"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Создает JWT access token
    
    Args:
        data: Данные для включения в токен (обычно {"sub": username})
        expires_delta: Время жизни токена. Если не указано, используется значение по умолчанию
        
    Returns:
        Закодированный JWT токен
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Создает JWT refresh token
    
    Args:
        data: Данные для включения в токен (обычно {"sub": username})
        
    Returns:
        Закодированный JWT refresh токен
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str, token_type: str = "access") -> dict:
    """
    Декодирует и валидирует JWT токен
    
    Args:
        token: JWT токен для декодирования
        token_type: Тип токена ("access" или "refresh")
        
    Returns:
        Декодированный payload токена
        
    Raises:
        HTTPException: Если токен невалиден или истек
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Проверяем тип токена
        if payload.get("type") != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token type. Expected {token_type}",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
            
        return payload
        
    except JWTError:
        raise credentials_exception


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """Получает пользователя по имени"""
    result = await db.execute(select(User).where(User.name == username))
    return result.scalar_one_or_none()


async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
    """
    Аутентифицирует пользователя по имени и паролю
    
    Args:
        db: Сессия базы данных
        username: Имя пользователя
        password: Пароль в открытом виде
        
    Returns:
        Объект User если аутентификация успешна, None в противном случае
    """
    user = await get_user_by_username(db, username)
    if not user:
        return None
    
    if not verify_password(password, user.password):
        return None
    
    return user


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Получает текущего аутентифицированного пользователя из JWT токена
    
    Args:
        token: JWT токен из заголовка Authorization
        db: Сессия базы данных
        
    Returns:
        Объект User
        
    Raises:
        HTTPException: Если токен невалиден или пользователь не найден
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token, token_type="access")
    username: str = payload.get("sub")
    
    if username is None:
        raise credentials_exception
    
    user = await get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Получает текущего активного пользователя (можно расширить проверкой is_active)
    
    Args:
        current_user: Текущий пользователь из get_current_user
        
    Returns:
        Объект User
    """
    # Здесь можно добавить проверку is_active, если добавите это поле в модель
    # if not current_user.is_active:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
