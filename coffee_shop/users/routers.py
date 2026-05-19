from typing import Annotated
from fastapi import APIRouter, Depends
from users.schemas import UserSchema
from security.dependencies import authenticate_user

router = APIRouter()

@router.get("/me")
def get_me(user: Annotated[UserSchema | None, Depends(authenticate_user)]):
    return user