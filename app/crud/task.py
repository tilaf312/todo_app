from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate
from typing import List


async def create_task(db: AsyncSession, task: TaskCreate, user_id: int) -> Task:
    """Создает новую задачу"""
    db_task = Task(**task.model_dump(), user_id=user_id)
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task


async def get_tasks(db: AsyncSession, user_id: int) -> List[Task]:
    """Получает все задачи пользователя"""
    result = await db.execute(
        select(Task).where(Task.user_id == user_id)
    )
    return list(result.scalars().all())


async def get_task(db: AsyncSession, task_id: int, user_id: int) -> Task | None:
    """Получает задачу по ID (только если она принадлежит пользователю)"""
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def update_task(
    db: AsyncSession,
    task_id: int,
    task_update: TaskUpdate,
    user_id: int
) -> Task | None:
    """Обновляет задачу"""
    task = await get_task(db, task_id, user_id)
    if not task:
        return None
    
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    await db.commit()
    await db.refresh(task)
    return task


async def delete_task(db: AsyncSession, task_id: int, user_id: int) -> bool:
    """Удаляет задачу"""
    task = await get_task(db, task_id, user_id)
    if not task:
        return False
    
    await db.delete(task)
    await db.commit()
    return True
