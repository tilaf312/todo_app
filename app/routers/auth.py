from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth.jwt import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
)
from app.schemas.auth import Token, TokenRefresh, LoginRequest
from app.config import settings
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token, summary="Вход в систему")
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Аутентификация пользователя и получение токенов
    
    - **username**: Имя пользователя
    - **password**: Пароль
    
    Возвращает access_token и refresh_token
    """
    user = await authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Создаем токены
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.name},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": user.name})
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/token", response_model=Token, summary="Вход через OAuth2 (для обратной совместимости)")
async def login_oauth2(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    OAuth2 совместимый endpoint для аутентификации
    
    Используется стандартная форма OAuth2PasswordRequestForm
    """
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.name},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": user.name})
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/refresh", response_model=Token, summary="Обновление токена")
async def refresh_token(
    token_data: TokenRefresh,
    db: AsyncSession = Depends(get_db)
):
    """
    Обновление access token с помощью refresh token
    
    - **refresh_token**: Refresh token для обновления
    
    Возвращает новую пару access_token и refresh_token
    """
    try:
        payload = decode_token(token_data.refresh_token, token_type="refresh")
        username: str = payload.get("sub")
        
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Невалидный refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Создаем новые токены
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": username},
            expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(data={"sub": username})
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/me", summary="Информация о текущем пользователе")
async def get_me(current_user = Depends(get_current_user)):
    """
    Получить информацию о текущем аутентифицированном пользователе
    """
    return {
        "id": current_user.id,
        "name": current_user.name,
        "username": current_user.name  # Для обратной совместимости
    }
