from fastapi import HTTPException
from fastapi import status
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import EmailStr
from pydantic import field_validator


class UserBaseSchema(BaseModel):
    username: str
    email: EmailStr

    @field_validator("username")
    def validate_username(cls, value):
        if len(value) < 4:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Username must be at least 4 characters long",
            )
        return value


class UserUpdateSchema(UserBaseSchema):
    is_active: bool


class UserUpdatePartialSchema(UserBaseSchema):
    username: str | None = None
    email: EmailStr | None = None
    is_active: bool | None = None


class UserSchema(UserBaseSchema):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UserCreateSchema(UserBaseSchema):
    password: str
