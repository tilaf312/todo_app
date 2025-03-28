from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
import bcrypt
from fastapi import HTTPException, status

def create_user(db: Session, user: UserCreate):
    existing = db.query(User).filter(User.name == user.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже существует"
        )

    hashed_password = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()
    db_user = User(name=user.name, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user



def get_user_by_name(db: Session, name: str):
    return db.query(User).filter(User.name == name).first()
