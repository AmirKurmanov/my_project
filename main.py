import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Literal
from fastapi import Depends
from typing import Annotated

app = FastAPI()

from fastapi.security.http import HTTPBasic, HTTPBasicCredentials
from fastapi import Depends, FastAPI, HTTPException, status

BasicSchema = HTTPBasic()


class UserSchema(BaseModel):
    name: str
    login: str

class AnimalCreateSchema(BaseModel):
    type: str
    name: str


class AnimalSchema(BaseModel):
    id: int
    type: str
    name: str


class AnimalUpdateSchema(BaseModel):
    type: str | None = None  
    name: str | None = None


def authenticate_user(
    credentials: Annotated[HTTPBasicCredentials | None, Depends(BasicSchema)],
) -> UserSchema | None:
    if credentials is None:
        return None

    if credentials.username != "admin" or credentials.password != "qwerty12":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    return UserSchema(name="Иван", login="admin")


@app.get("/users/me")
def get_me(user: Annotated[UserSchema, Depends(authenticate_user)]) -> UserSchema:
    return user

@app.post("/animals")
def create_animal(body: AnimalCreateSchema) -> AnimalSchema:
    return AnimalSchema(id=1, type=body.type, name=body.name)


@app.get("/animals/{id}")
def get_animal(id: int) -> AnimalSchema:
    return AnimalSchema(id=1, type="cat", name="Мурзик")


@app.get("/animals")
def get_all_animals(
    name: str | None = None, type: str | None = None
) -> list[AnimalSchema]:
    return [
        AnimalSchema(id=1, type="cat", name="Мурзик"),
        AnimalSchema(id=2, type="cat", name="Барсик"),
        AnimalSchema(id=3, type="dog", name="Шарик")
    ]


@app.put("/animals/{id}")
def update_animal(id: int, body: AnimalUpdateSchema) -> AnimalSchema:
    return AnimalSchema(
        id=id,
        type=body.type if body.type is not None else "cat",  
        name=body.name if body.name is not None else "Мурзик"
    )




if __name__ == "__main__":
    uvicorn.run(app)