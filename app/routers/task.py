from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskOut, TaskUpdate
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


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    db.delete(task)
    db.commit()
    return None


@router.put("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    updated_task: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    task.name = updated_task.name
    task.description = updated_task.description
    db.commit()
    db.refresh(task)
    return task