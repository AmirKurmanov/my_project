from typing import Annotated

from pydantic import BaseModel, StringConstraints

type UserLogin = Annotated[str, StringConstraints(min_length=1, max_length=100)]
type UserPassword = Annotated[str, StringConstraints(min_length=8, max_length=100)]


class UserSchema(BaseModel):
    id: int
    login: str


class UserCreate(BaseModel):
    login: UserLogin
    password: UserPassword


class UserUpdate(BaseModel):
    login: UserLogin
    password: UserPassword | None = None