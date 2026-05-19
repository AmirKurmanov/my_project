from typing import Annotated
import jwt
from fastapi import Depends, HTTPException
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer
from core.config import SECRET_KEY
from users.schemas import UserSchema

BearerSchema = HTTPBearer()

def authenticate_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(BearerSchema)],
) -> UserSchema | None:
    if credentials is None:
        return None

    try:
        token = credentials.credentials
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=["HS256"])
        return UserSchema(id=payload["id"], login=payload["login"])
    except jwt.InvalidTokenError:
        return None