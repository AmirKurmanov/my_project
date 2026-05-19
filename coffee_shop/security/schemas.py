from pydantic import BaseModel

from coffee_shop.users.schemas import UserLogin, UserPassword


class LoginRequest(BaseModel):
    login: UserLogin
    password: UserPassword


class LoginResponse(BaseModel):
    token: str
