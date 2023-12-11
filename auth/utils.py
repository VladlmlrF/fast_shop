from datetime import datetime
from datetime import timedelta
from typing import Annotated

from fastapi import Depends
from fastapi import Form
from fastapi import HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose import JWTError
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import auth_settings
from core.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_password_hash(password: str) -> str:
    """Hash the password"""
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Password verification"""
    return pwd_context.verify(password, hashed_password)


async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    """Get user by username"""
    statement = select(User).where(User.username == username)
    user: User | None = await session.scalar(statement=statement)
    return user


def create_access_token(
    payload: dict,
    algorithm: str = auth_settings.algorithm,
    private_key: str = auth_settings.private_key_path.read_text(),
    expires_timedelta: timedelta | None = None,
    expire_minutes: int = auth_settings.access_token_expire_minutes,
) -> str:
    """Encode token"""
    to_encode = payload.copy()
    now = datetime.utcnow()
    if expires_timedelta:
        expire = now + expires_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(claims=to_encode, key=private_key, algorithm=algorithm)
    return encoded_jwt


def decode_access_token(
    token: str,
    public_key: str = auth_settings.public_key_path.read_text(),
    algorithm: str = auth_settings.algorithm,
) -> dict:
    """Decode token"""
    decoded = jwt.decode(token=token, key=public_key, algorithms=[algorithm])
    return decoded


async def authenticate_user(
    session: AsyncSession, username: str = Form(), password: str = Form()
) -> User | None:
    """Checking user authentication"""
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid username or password"
    )
    user = await get_user_by_username(session=session, username=username)
    if not user:
        raise unauthed_exc
    if not verify_password(password=password, hashed_password=user.hashed_password):
        raise unauthed_exc
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="user inactive"
        )
    return user


async def get_current_user(
    session: AsyncSession,
    token: Annotated[str, Depends(oauth2_scheme)],
):
    """Get current user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload: dict = decode_access_token(token=token)
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = await get_user_by_username(session, username)
        if not user:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception
