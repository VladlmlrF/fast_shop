from fastapi import HTTPException
from fastapi import status
from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from auth.utils import get_password_hash
from auth.utils import get_user_by_username
from core.models import Role
from core.models import User
from users.schemas import UserCreateSchema
from users.schemas import UserUpdatePartialSchema


async def create_user(session: AsyncSession, user: UserCreateSchema) -> User:
    """Create user"""
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
    )
    try:
        session.add(new_user)
        await session.commit()
        return new_user
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User with that username or email already exists!",
        )


async def create_super_admin(session: AsyncSession, user: UserCreateSchema) -> User:
    """Create Super Admin"""
    super_admin = User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        role=Role.SUPER_ADMIN,
    )
    session.add(super_admin)
    await session.commit()
    return super_admin


async def create_admin(session: AsyncSession, username: str, make_admin: bool):
    """Change admin rights to the user"""
    user = await get_user_by_username(session=session, username=username)
    if user:
        if make_admin:
            user.role = Role.ADMIN
            await session.commit()
            return user
        else:
            user.role = Role.ORDINARY_USER
            await session.commit()
            return user
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"User {username} not found"
    )


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
    user_update: UserUpdatePartialSchema,
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


async def deactivate_user(
    session: AsyncSession,
    username: str,
):
    """Deactivate user"""
    user = await get_user_by_username(session=session, username=username)
    if user:
        if user.is_active:
            user.is_active = False
            await session.commit()
            return user
        else:
            user.is_active = True
            await session.commit()
            return user
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"User {username} not found"
    )
