from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # JWT настройки
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: Optional[str] = "sqlite+aiosqlite:///./test.db"
    DB_ECHO: bool = False  # Логирование SQL запросов
    DB_POOL_SIZE: int = 5  # Размер пула соединений
    DB_MAX_OVERFLOW: int = 10  # Максимальное количество соединений сверх pool_size
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

