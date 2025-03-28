from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserOut
from app.schemas.auth import AuthRequest, AuthResponse
from app.crud import user as crud_user
from app.crud import auth as crud_auth

router = APIRouter()


@router.post("/", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return crud_user.create_user(db, user)
