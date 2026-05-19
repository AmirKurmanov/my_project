from fastapi import FastAPI


def setup_app():
    app = FastAPI()

    from coffee_shop.security.routers import router as security_router
    from coffee_shop.users.routers import router as user_router

    app.include_router(security_router)
    app.include_router(user_router)

    return app