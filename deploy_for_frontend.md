# Подготовка бэкенда для фронтенда

- создать файл docker-compose.yml
```yml
services:
  postgres:
    container_name: postgres_todo_db
    restart: always
    image: postgres:18-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: todo_db
    ports:
      - "9001:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init_scripts:/docker-entrypoint-initdb.d  # Монтирование скриптов
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d todo_db"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - todo_network

  todo-service:
    image: nanku/todo-api:latest
    restart: always
    pull_policy: always
    container_name: todo-service
    env_file:
      - ./.env
    environment:
      - PG_DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/todo_db
    ports:
      - "8080:8000"
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - todo_network

volumes:
  postgres_data:

networks:
  todo_network:
    driver: bridge
```
- создать .env
```
SECRET_KEY=20b5faf8e6b59a8fd21e356192fc0191d48af6874a2c9874aaf174840a4639f5
ALGORITHM=HS256

#POSTGRES
PG_DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:9001/todo_db"
```
- запустить
```
docker compose up -d --build
```
- открыть url
```
http://localhost:8080/docs
```