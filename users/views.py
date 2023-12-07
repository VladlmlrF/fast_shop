from fastapi import APIRouter
from fastapi import Depends
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from .crud import create_user
from .schemas import UserCreateSchema
from .schemas import UserSchema
from core.models import db_helper

router = APIRouter(tags=["User"])


@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_new_user(
    user_in: UserCreateSchema,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await create_user(session=session, user=user_in)
