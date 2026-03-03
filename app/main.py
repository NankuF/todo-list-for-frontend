from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users, todos

app = FastAPI(
    title="ToDo list",
    version="0.1.0"
)

# --- НАСТРОЙКА CORS ---
# Разрешаем запросы только с конкретного домена фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # React dev server
        "http://localhost:5174",       # Vite dev server
        "http://127.0.0.1:5174",
        "http://localhost:80",         # Nginx в продакшене
        "https://your-domain.com",     # Ваш домен
    ],
    allow_credentials=True,           # Разрешить cookies/авторизацию
    allow_methods=["*"],              # Разрешить все методы (GET, POST, PUT, DELETE)
    allow_headers=["*"],              # Разрешить все заголовки
)

app.include_router(users.router)
app.include_router(todos.router)

@app.get("/")
async def root():
    return {"message": "test"}