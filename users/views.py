from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud
from .schemas import UserCreateSchema
from .schemas import UserSchema
from .schemas import UserUpdatePartialSchema
from .schemas import UserUpdateSchema
from core.models import db_helper

router = APIRouter(tags=["User"])


@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_new_user(
    user_in: UserCreateSchema,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.create_user(session=session, user=user_in)


@router.get("/", response_model=list[UserSchema])
async def get_users(
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.get_users(session=session)


@router.get("/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: int, session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    user = await crud.get_user(session=session, user_id=user_id)
    if user:
        return user
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found!"
    )


@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    user_update: UserUpdateSchema,
    user_id: int,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    user = await crud.get_user(session=session, user_id=user_id)
    if user:
        return await crud.update_user(
            session=session, user=user, user_update=user_update
        )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found!"
    )


@router.patch("/{user_id}", response_model=UserSchema)
async def update_user_partial(
    user_update: UserUpdatePartialSchema,
    user_id: int,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    user = await crud.get_user(session=session, user_id=user_id)
    if user:
        return await crud.update_user(
            session=session, user=user, user_update=user_update, partial=True
        )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found!"
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int, session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    user = await crud.get_user(session=session, user_id=user_id)
    if user:
        await crud.delete_user(session=session, user=user)
        return None
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found!"
    )
