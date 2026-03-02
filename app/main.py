from fastapi import FastAPI
from app.routers import users, todos

app = FastAPI(
    title="ToDo list",
    version="0.1.0"
)

app.include_router(users.router)
app.include_router(todos.router)

@app.get("/")
async def root():
    return {"message": "test"}