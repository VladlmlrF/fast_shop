from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from auth.utils import get_password_hash
from core.models import User
from users.schemas import UserCreateSchema
from users.schemas import UserUpdatePartialSchema
from users.schemas import UserUpdateSchema


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


async def get_users(session: AsyncSession) -> list[User]:
    """Get all users"""
    statement = select(User).order_by(User.id)
    result: Result = await session.execute(statement=statement)
    users = result.scalars().all()
    return list(users)


async def get_user(session: AsyncSession, user_id: int) -> User | None:
    """Get user by user_id"""
    return await session.get(User, user_id)


async def update_user(
    session: AsyncSession,
    user: User,
    user_update: UserUpdateSchema | UserUpdatePartialSchema,
    partial: bool = False,
) -> User:
    """Update user"""
    for name, value in user_update.model_dump(exclude_unset=partial).items():
        setattr(user, name, value)
    await session.commit()
    return user


async def delete_user(session: AsyncSession, user: User) -> None:
    """Delete user"""
    await session.delete(user)
    await session.commit()
