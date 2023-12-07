from sqlalchemy.ext.asyncio import AsyncSession

from auth.utils import get_password_hash
from core.models import User
from users.schemas import UserCreateSchema


async def create_user(session: AsyncSession, user: UserCreateSchema) -> User:
    """Create user"""
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
    )
    session.add(new_user)
    await session.commit()
    return new_user
