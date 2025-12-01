from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.user import UserCreate, UserOut
from app.auth.jwt import get_password_hash


def create_user(db: Session, user: UserCreate) -> UserOut:
    """Создает нового пользователя с хешированным паролем"""
    # Проверяем, существует ли пользователь с таким именем
    existing_user = db.query(User).filter(User.name == user.name).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже существует"
        )
    
    # Хешируем пароль перед сохранением
    hashed_password = get_password_hash(user.password)
    
    # Создаем нового пользователя
    db_user = User(
        name=user.name,
        password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return UserOut(id=db_user.id, name=db_user.name)

