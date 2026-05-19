from fastapi import APIRouter

from coffee_shop.security.schemas import LoginRequest, LoginResponse

router = APIRouter()


@router.post("/login")
async def login(body: LoginRequest) -> LoginResponse: ...