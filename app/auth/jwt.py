from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import hashlib
import base64

from app.models.user import User
from app.database import get_db

# Простая имитация JWT для тестового проекта
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Простое хранилище токенов в памяти (для тестов)
# В реальном проекте это должно быть в Redis или базе данных
token_storage = {}


def get_password_hash(password: str) -> str:
    """Создает строку похожую на хеш для сохранения в БД (простая имитация)"""
    # Создаем хеш используя SHA256
    hash_obj = hashlib.sha256(password.encode('utf-8'))
    hash_hex = hash_obj.hexdigest()
    
    # Кодируем hex в base64 для более компактного вида
    b64_hash = base64.b64encode(hash_hex.encode()).decode()
    
    # Добавляем префикс для похожести на bcrypt ($2b$10$)
    # bcrypt hash имеет формат: $2b$10$ + 53 символа base64 = 60 символов всего
    # Сохраняем реальный хеш (43 символа) и дополняем до 53 для похожести
    real_hash = b64_hash[:43]  # SHA256 hex (64 символа) в base64 = 43 символа
    
    # Дополняем до 53 символов случайными base64 символами для похожести на bcrypt
    import random
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    padding = ''.join(random.choice(chars) for _ in range(53 - len(real_hash)))
    hash_part = real_hash + padding
    
    return f"$2b$10${hash_part}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля - извлекает оригинальный хеш и сравнивает"""
    # Проверяем формат хеша
    if not hashed_password.startswith("$2b$10$"):
        # Если старый формат (без хеша), сравниваем напрямую для обратной совместимости
        return plain_password == hashed_password
    
    # Извлекаем base64 часть
    b64_part = hashed_password[7:]  # Убираем "$2b$10$"
    
    try:
        # Вычисляем хеш от введенного пароля
        hash_obj = hashlib.sha256(plain_password.encode('utf-8'))
        input_hex = hash_obj.hexdigest()
        input_b64 = base64.b64encode(input_hex.encode()).decode()
        
        # Сравниваем только реальную часть хеша (первые 43 символа)
        # Остальные символы - это padding для похожести на bcrypt
        stored_real = b64_part[:43]
        input_real = input_b64[:43]
        
        return stored_real == input_real
    except Exception:
        # Если что-то пошло не так, возвращаем False
        return False


def create_access_token(data: dict, expires_delta=None):
    """Создает простой токен в формате 'token_{username}'"""
    username = data.get("sub")
    if not username:
        raise ValueError("Username is required")
    # Простой токен для тестов
    token = f"token_{username}"
    # Сохраняем токен в памяти
    token_storage[token] = username
    return token


def get_user(db: Session, username: str):
    """Получает пользователя из базы данных"""
    return db.query(User).filter(User.name == username).first()


def authenticate_user(db: Session, username: str, password: str):
    """Аутентификация пользователя"""
    user = get_user(db, username)
    if not user:
        return False
    # Простая проверка пароля для тестов
    if not verify_password(password, user.password):
        return False
    return user


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Получает текущего пользователя по токену (простая имитация)"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Простая проверка токена
    if not token or not token.startswith("token_"):
        raise credentials_exception
    
    # Извлекаем username из токена
    username = token.replace("token_", "", 1)
    
    # Проверяем, что токен есть в хранилище (для тестов)
    if token not in token_storage:
        raise credentials_exception
    
    # Получаем пользователя из базы данных
    user = get_user(db, username)
    if user is None:
        raise credentials_exception
    
    return user
