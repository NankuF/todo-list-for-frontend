from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_async_db
from app.models import Task, User
from app.schemas import TaskCreateDTO, TaskDTO

router = APIRouter(prefix="/todos", tags=["todos"])


@router.get("/me", response_model=list[TaskDTO], status_code=status.HTTP_200_OK)
async def get_todos_by_user(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
):
    """
    Просмотр списка задач пользователя.
    """
    tasks = (
        await session.scalars(
            select(Task).where(Task.is_active, Task.user_id == current_user.id)
        )
    ).all()

    return tasks


@router.get("/me/{todo_id}", response_model=TaskDTO, status_code=status.HTTP_200_OK)
async def get_todo(
    todo_id: int,
    session: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """
    Просмотр задачи по id.
    """
    task = await session.scalar(
        select(Task).where(
            Task.is_active, Task.id == todo_id, Task.user_id == current_user.id
        )
    )
    if not task:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found or inactive.")

    return task


@router.post("/me", response_model=TaskDTO, status_code=status.HTTP_201_CREATED)
async def create_todo(
    payload: TaskCreateDTO,
    session: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """
    Создание задачи.
    """
    task = Task(**payload.model_dump(), user_id=current_user.id)
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


@router.put("/me/{todo_id}", response_model=TaskDTO, status_code=status.HTTP_200_OK)
async def update_todo(
    todo_id: int,
    payload: TaskCreateDTO,
    session: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """
    Обновление задачи по id.
    """
    task = await session.scalar(
        select(Task).where(
            Task.is_active, Task.id == todo_id, Task.user_id == current_user.id
        )
    )
    if not task:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found or inactive.")

    for key,value in payload.model_dump(exclude_unset=True).items():
        setattr(task, key, value)

    await session.commit()
    await session.refresh(task)
    return task

@router.delete("/me/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
):
    """
    Удаление задачи по id.
    """
    task = await session.scalar(
        select(Task).where(
            Task.is_active, Task.user_id == current_user.id, Task.id == todo_id
        )
    )
    if task is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found or inactive.")

    task.is_active = False
    await session.commit()
    
