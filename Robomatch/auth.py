from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta


users = []

pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto"
)

SECRET_KEY = "YFOQ^&wfdw6^&AWFD95qfowd8gq67f7WFD965efdo7F"
ALGORITHM = "HS256"

class RegisterRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str


def register_user(data: RegisterRequest):
    for user in users:
        if user["username"] == data.username:
            return {
                "success": False, 
                "message": "Пользователь уже существует"
            }
    password_hash = pwd_context.hash(data.password)
            
    users.append({
        "username": data.username, 
        "password_hash": password_hash
    })


    return {
        "success": True, 
        "message": "Пользователь зарегистрирован"
    }

def create_access_token(username: str):
    payload = {
        "sub": username
    }

    token = jwt.encode(
        payload, 
        SECRET_KEY, 
        algorithm=ALGORITHM
    )
    return token

def login_user(data: LoginRequest):
    for user in users:
        if user["username"] == data.username and user["password"] == data.password:
                token = create_access_token(data.username)
                return {
                    "success": True, 
                    "access_token": token, 
                    "token_type": "bearer"
                }
    return {
        "success": False, 
        "message": "Неверный логин или пароль"
    }    