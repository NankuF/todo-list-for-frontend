
from pydantic import AwareDatetime, BaseModel, ConfigDict, EmailStr, Field

class TaskCreateDTO(BaseModel):
    """
    Модель для создания задачи.
    Используется в POST запросе.
    """
    title: str = Field(min_length=1, max_length=100, description="Название задачи")
    description: str = Field(description="Описание задачи")
    priority: str = Field(default="low", pattern="^(low|high)$", description="Приоритет задачи")
    is_completed: bool = Field(default=False, description="Завершенность задачи")

class TaskDTO(TaskCreateDTO):
    """
    Модель для ответа с данными задачи.
    Используется в GET запросе.
    """
    id: int = Field(description="Уникальный идентификатор задачи")

    is_active: bool = Field(description="Активность задачи")
    created_at: AwareDatetime = Field(description="Дата и время создания задачи в UTC")
    updated_at: AwareDatetime = Field(description="Дата и время обновления задачи в UTC")
    model_config = ConfigDict(from_attributes=True)

class ChangePasswordDTO(BaseModel):
    """
    Модель для обновления пароля пользователя.
    Используется в PUT запросе.
    """
    current_password: str = Field(min_length=8, description="Пароль (минимум 8 символов)")
    new_password: str = Field(min_length=8, description="Новый пароль (минимум 8 символов)")

class ChangeEmailDTO(BaseModel):
    """
    Модель для обновления email пользователя.
    Используется в PUT запросе.
    """
    email: EmailStr = Field(description="Email пользователя")

class UserDeleteDTO(BaseModel):
    """
    Модель для удаления  пользователя.
    Используется в DELETE запросе.
    """
    current_password: str = Field(min_length=8, description="Пароль (минимум 8 символов)")

class UserCreateDTO(BaseModel):
    """
    Модель для создания пользователя.
    Используется в POST запросе.
    """
    email: EmailStr = Field(description="Email пользователя")
    password: str = Field(min_length=8, description="Пароль (минимум 8 символов)")
    role: str = Field(default="user", pattern="^(user)$", description="Роль: 'user'")

class UserUpdateDTO(BaseModel):
    """
    Модель для  обновления пользователя.
    Используется в PUT запросе.
    """
    role: str = Field(default="user", pattern="^(user)$", description="Роль: 'user'")

class UserDTO(BaseModel):
    """
    Модель для ответа с данными пользователя.
    Используется в GET-запросах.
    """
    id: int = Field(description="Уникальный идентификатор пользователя")
    email: EmailStr = Field(description="Email пользователя")
    role: str = Field(description="Роль пользователя")

    is_active: bool = Field(description="Активность пользователя")
    created_at: AwareDatetime = Field(description="Дата и время создания пользователя в UTC")
    updated_at: AwareDatetime = Field(description="Дата и время обновления пользователя в UTC")
    model_config = ConfigDict(from_attributes=True)
