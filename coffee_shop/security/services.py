from coffee_shop.security.schemas import LoginRequest, LoginResponse


class SecurityService:
    def __init__(self): ...

    async def login(self, body: LoginRequest) -> LoginResponse: ...