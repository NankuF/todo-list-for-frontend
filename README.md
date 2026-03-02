# TODO list

# For backend developer
uv init
uv venv
uv add fastapi
uv add uvicorn[standard]
uv add acyncpg
uv add sqlalchemy
uv add alembic
uv add pydantic[email]    - for EmailStr
uv add python-multipart   - for auth

auth:
uv add passlib  (устарела, сменить на свежую)
uv add pyjwt   - for jwt

## Alembic
uv add alembic
alembic init -t async app/migrations
app/migrations/env.py ->
```
from app.database import Base
from app import models

def run_migrations_offline() -> None:
...
    context.configure(
        url=PG_DATABASE_URL,
        ...
    )

async def run_async_migrations() -> None:
...
    connectable = async_engine_from_config(
        {"sqlalchemy.url": PG_DATABASE_URL},
        ...
    )
```
ignore alembic.ini
alembic revision --autogenerate  -m "Create user and todos tables"   - создание файла миграции
alembic upgrade head - применены миграции к бд.


## Сделано
- в ./init_scripts лежат скрипты для создания базы данных при первом запуске из docker-compose.yml

# Сделать
Спрятать в .env данные подключения к postgres.
Использовать в docker-compose и DATABASE_URL.


# Алгоритм работы
Пользователь регистрируется
Затем аутентифицируется
Под своей УЗ может выполнять CRUD по задачам.

Пользователь может:
- Зарегистрироваться.
- Аутентифицироваться. (токены нигде не сохраняются, ни на фронте, ни на бэке, только в swagger)
- Обновить свой пароль.
- Обновить свой email.
- Посмотреть свой профиль.
- Удаление своего профиля (частично)
- Использовать CRUD для задач.
- !!! НЕ может выйти из системы (unlogin + invalidate access_token+refresh_token)