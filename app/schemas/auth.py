from pydantic import BaseModel, Field
from typing import Optional


class Token(BaseModel):
    """Схема ответа с токенами"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Тип токена")


class TokenData(BaseModel):
    """Данные из JWT токена"""
    username: Optional[str] = None


class TokenRefresh(BaseModel):
    """Схема запроса на обновление токена"""
    refresh_token: str = Field(..., description="Refresh token для обновления")


class LoginRequest(BaseModel):
    """Схема запроса на вход"""
    username: str = Field(..., min_length=1, description="Имя пользователя")
    password: str = Field(..., min_length=1, description="Пароль")


class AuthRequest(BaseModel):
    """Схема запроса аутентификации (для обратной совместимости)"""
    name: str
    password: str


class AuthResponse(BaseModel):
    """Схема ответа аутентификации (для обратной совместимости)"""
    message: str
