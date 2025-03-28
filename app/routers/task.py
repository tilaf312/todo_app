from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskOut
from app.auth.jwt import get_current_user

router = APIRouter()


@router.post("/", response_model=TaskOut)
def create_task(
        task: TaskCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    db_task = Task(
        name=task.name,
        description=task.description,
        user_id=current_user.id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.get("/", response_model=List[TaskOut])
def get_tasks(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return db.query(Task).filter(Task.user_id == current_user.id).all()
