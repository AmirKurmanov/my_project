from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from coffee_shop.users.models import User
from coffee_shop.users.schemas import UserCreateSchema
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user_data: UserCreateSchema):
    hashed_password = pwd_context.hash(user_data.password)
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user