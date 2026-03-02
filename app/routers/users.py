from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.database import get_async_db
from app.models import User
from app.models.todos import Task
from app.schemas import (
    ChangeEmailDTO,
    ChangePasswordDTO,
    UserCreateDTO,
    UserDTO,
    UserDeleteDTO,
    UserUpdateDTO,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserDTO, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreateDTO, session: AsyncSession = Depends(get_async_db)
):
    """
    Регистрация пользователя.
    """
    user = (
        await session.scalars(
            select(User).where(User.email == payload.email, User.is_active)
        )
    ).first()
    if user:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already exist.")

    db_user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=payload.role,
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


@router.get("/me", response_model=UserDTO, status_code=status.HTTP_200_OK)
async def get_user(
    current_user: User = Depends(get_current_user),
):
    """
    Просмотр профиля пользователя.
    """
    return current_user


@router.put("/me", response_model=UserDTO, status_code=status.HTTP_200_OK)
async def update_user(
    payload: UserUpdateDTO,
    session: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """
    Обновление профиля пользователя.
    Пароль и email обновляются через другие endpoints.
    """
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(current_user, key, value)

    await session.commit()
    await session.refresh(current_user)
    return current_user


@router.put("/me/change_email", status_code=status.HTTP_200_OK)
async def change_email(
    payload: ChangeEmailDTO,
    session: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """
    Обновление email пользователя.
    """
    # Проверка на совпадение email
    if payload.email == current_user.email:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Emails must be different.")
    # Поиск email в базе данных среди всех пользователей, включая деактивированных.
    user = await session.scalar(select(User).where(User.email == payload.email))
    if user:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already exist.")

    current_user.email = payload.email
    await session.commit()
    return {"message": "email changed"}


@router.put("/me/change_password", status_code=status.HTTP_200_OK)
async def change_password(
    payload: ChangePasswordDTO,
    session: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """
    Обновление пароля пользователя.
    """
    # Валидация текущего пароля
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Incorrect password.")
    # Проверка на совпадение паролей
    if verify_password(payload.new_password, current_user.hashed_password):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Passwords must be different.")

    current_user.hashed_password = hash_password(payload.new_password)
    # from sqlalchemy import inspect
    # print(inspect(current_user).persistent)
    # session.add не требуется, тк inspect(current_user).persistent=True, т.е объект в текущей сессии,
    # в статус persistent сurrent_user перешел тк внутри get_current_user был выполнен scalar.
    # session.add(current_user)  - Метод add() необходим только для новых объектов (состояние Transient).

    await session.commit()
    # await session.refresh(current_user) - не нужен, тк не возвращаем данные пользователя.
    return {"message": "password changed"}


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    payload: UserDeleteDTO,
    session: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """
    Мягкое удаление пользователя (soft delete)
    """
    # Валидация текущего пароля
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Incorrect password.")

    # Деактивация дочерних объектов в императивном стиле (отлично для массовых изменений)
    # в обход тригеров и валидаторов модели Task (если их нет - ок)
    await session.execute(update(Task).where(Task.user_id==User.id).values(is_active=False))
    # TODO Деактивация токенов (blacklist)

    current_user.is_active = False
    await session.commit()
    return

@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_async_db),
):
    """
    Аутентифицирует пользователя и возвращает JWT с email, role и id.
    """
    user = (
        await session.scalars(
            select(User).where(User.email == form_data.username, User.is_active)
        )
    ).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "id": user.id}
    )
    refresh_token = create_refresh_token(
        data={"sub": user.email, "role": user.role, "id": user.id}
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
