from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Response
from fastapi import status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import TokenDataSchema
from .utils import authenticate_user
from .utils import create_access_token
from core.models import db_helper

router = APIRouter(tags=["Auth"])


@router.post("/login", response_model=TokenDataSchema)
async def login_for_access_token(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    user = await authenticate_user(
        session=session, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = {"sub": user.username, "username": user.username, "email": user.email}
    token = create_access_token(payload=payload)
    response.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True)
    return TokenDataSchema(access_token=token, token_type="Bearer")
