from typing import Annotated
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from security.routers import router as security_router
from users.routers import router as users_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Подключаем маршруты
app.include_router(security_router, tags=["auth"])
app.include_router(users_router, tags=["users"])

if __name__ == "__main__":
    uvicorn.run(app)