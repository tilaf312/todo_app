from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import hashlib
import secrets

from app.models.user import User
from app.database import get_db

# Простая имитация JWT для тестового проекта
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Простое хранилище токенов в памяти (для тестов)
# В реальном проекте это должно быть в Redis или базе данных
token_storage = {}


def get_password_hash(password: str) -> str:
    """Создает хеш пароля для сохранения в БД (простая имитация)"""
    # Используем SHA256 для создания хеша
    hash_obj = hashlib.sha256(password.encode('utf-8'))
    hash_hex = hash_obj.hexdigest()
    
    # Добавляем соль для безопасности (генерируем случайную строку)
    salt = secrets.token_hex(16)  # 32 символа в hex
    
    # Создаем финальный хеш: соль + хеш пароля
    combined = salt + hash_hex
    final_hash = hashlib.sha256(combined.encode('utf-8')).hexdigest()
    
    # Формат: $hash$salt$final_hash (для удобства хранения)
    return f"$hash${salt}${final_hash}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля - сравнивает хеш введенного пароля с сохраненным"""
    try:
        # Проверяем формат хеша
        if not hashed_password.startswith("$hash$"):
            # Если старый формат (без хеша), сравниваем напрямую для обратной совместимости
            return plain_password == hashed_password
        
        # Извлекаем соль и финальный хеш
        parts = hashed_password.split("$")
        if len(parts) != 4:  # ['', 'hash', 'salt', 'final_hash']
            return False
        
        salt = parts[2]
        stored_hash = parts[3]
        
        # Вычисляем хеш от введенного пароля
        password_hash = hashlib.sha256(plain_password.encode('utf-8')).hexdigest()
        
        # Комбинируем соль с хешем пароля
        combined = salt + password_hash
        computed_hash = hashlib.sha256(combined.encode('utf-8')).hexdigest()
        
        # Сравниваем хеши
        return stored_hash == computed_hash
    except Exception:
        # Если что-то пошло не так, возвращаем False
        return False


def create_access_token(data: dict, expires_delta=None):
    """Создает простой токен (имитация JWT)"""
    username = data.get("sub")
    if not username:
        raise ValueError("Username is required")
    
    # Генерируем случайный токен
    token = secrets.token_urlsafe(32)
    
    # Сохраняем токен в памяти с привязкой к username
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
    
    # Проверяем пароль
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
    
    # Проверяем наличие токена
    if not token:
        raise credentials_exception
    
    # Проверяем, что токен есть в хранилище
    if token not in token_storage:
        raise credentials_exception
    
    # Получаем username из хранилища
    username = token_storage[token]
    
    # Получаем пользователя из базы данных
    user = get_user(db, username)
    if user is None:
        raise credentials_exception
    
    return user
