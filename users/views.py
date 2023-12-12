from typing import TYPE_CHECKING

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud
from .schemas import UserCreateSchema
from .schemas import UserSchema
from .schemas import UserUpdatePartialSchema
from auth.utils import get_current_user_name
from auth.utils import get_user_by_username
from core.models import db_helper

if TYPE_CHECKING:
    from core.models import User

router = APIRouter(tags=["User"])


@router.post(
    "/create_super_admin",
    response_model=UserSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_super_admin(
    user_in: UserCreateSchema,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.create_super_admin(session=session, user=user_in)


@router.post(
    "/activate_admin", response_model=UserSchema, status_code=status.HTTP_201_CREATED
)
async def activate_admin(
    username: str,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
    current_user_name: str = Depends(get_current_user_name),
):
    current_user: User | None = await get_user_by_username(
        session=session, username=current_user_name
    )
    if current_user.is_super_admin and username != current_user_name:
        return await crud.create_admin(
            session=session, username=username, make_admin=True
        )
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")


@router.post(
    "/deactivate_admin", response_model=UserSchema, status_code=status.HTTP_201_CREATED
)
async def deactivate_admin(
    username: str,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
    current_user_name: str = Depends(get_current_user_name),
):
    current_user: User | None = await get_user_by_username(
        session=session, username=current_user_name
    )
    if current_user.is_super_admin and username != current_user_name:
        return await crud.create_admin(
            session=session, username=username, make_admin=False
        )
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")


@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_new_user(
    user_in: UserCreateSchema,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.create_user(session=session, user=user_in)


@router.get("/", response_model=list[UserSchema])
async def get_users(
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
    current_user_name: str = Depends(get_current_user_name),
):
    current_user: User | None = await get_user_by_username(
        session=session, username=current_user_name
    )
    if current_user and (current_user.is_admin or current_user.is_super_admin):
        return await crud.get_users(session=session)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")


@router.get("/{username}", response_model=UserSchema)
async def get_user(
    username: str,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
    current_user_name: str = Depends(get_current_user_name),
):
    user_not_found_exc = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"User {username} not found!"
    )
    user = await crud.get_user_by_username(session=session, username=username)
    if user:
        if username == current_user_name:
            return user
        current_user: User | None = await get_user_by_username(
            session=session, username=current_user_name
        )
        if current_user.is_admin or current_user.is_super_admin:
            return user
        raise user_not_found_exc
    raise user_not_found_exc


@router.patch("/{username}", response_model=UserSchema)
async def update_user_partial(
    user_update: UserUpdatePartialSchema,
    username: str,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
    current_user_name: str = Depends(get_current_user_name),
):
    user_not_found_exc = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"User {username} not found!"
    )
    user = await crud.get_user_by_username(session=session, username=username)
    if user:
        if username == current_user_name:
            return await crud.update_user(
                session=session, user=user, user_update=user_update, partial=True
            )
        raise user_not_found_exc
    raise user_not_found_exc


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    username: str,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
    current_user_name: str = Depends(get_current_user_name),
):
    user_not_found_exc = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"User {username} not found!"
    )
    current_user: User | None = await get_user_by_username(
        session=session, username=current_user_name
    )
    if current_user.is_super_admin:
        user = await crud.get_user_by_username(session=session, username=username)
        if user:
            await crud.delete_user(session=session, user=user)
            return None
        raise user_not_found_exc
    raise user_not_found_exc


@router.post("/deactivate_user", response_model=UserSchema)
async def deactivate_user(
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
    current_user_name: str = Depends(get_current_user_name),
):
    current_user: User | None = await get_user_by_username(
        session=session, username=current_user_name
    )
    if not current_user.is_super_admin and not current_user.is_admin:
        return await crud.deactivate_user(session=session, username=current_user_name)
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Unable to deactivate this user"
    )
