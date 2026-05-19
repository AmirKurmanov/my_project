from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from coffee_shop.core.db import DatabaseManager, get_db
from coffee_shop.users.schemas import UserCreateSchema, UserResponseSchema
from coffee_shop.users.services import get_user_by_username, get_user_by_email, create_user

# Создаём менеджер БД
db_manager = DatabaseManager(
    "postgresql+asyncpg://admin:qwerty12@db:5432/coffee_shop"
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with db_manager:
        print("Database connected")
        yield
        print("Database disconnected")

app = FastAPI(title="Coffee Shop API", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

@app.get("/")
async def root():
    return {"message": "Welcome to Coffee Shop API"}

@app.post("/register", response_model=UserResponseSchema, status_code=201)
async def register(user_data: UserCreateSchema, db: AsyncSession = Depends(get_db)):
    existing_user = await get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(400, f"User '{user_data.username}' already exists")
    
    existing_email = await get_user_by_email(db, user_data.email)
    if existing_email:
        raise HTTPException(400, f"Email '{user_data.email}' already exists")
    
    new_user = await create_user(db, user_data)
    return new_user

@app.get("/users/{username}", response_model=UserResponseSchema)
async def get_user(username: str, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_username(db, username)
    if not user:
        raise HTTPException(404, f"User '{username}' not found")
    return user

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)