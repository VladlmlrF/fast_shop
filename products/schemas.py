from fastapi import HTTPException
from fastapi import status
from pydantic import BaseModel
from pydantic import field_validator


class ProductBaseSchema(BaseModel):
    name: str
    manufacturer: str
    description: str
    price: int

    @field_validator("price")
    def validate_price(cls, value):
        if value < 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="The price should not be less than zero!",
            )
        return value


class ProductCreateSchema(ProductBaseSchema):
    pass


class ProductUpdatePartialSchema(ProductBaseSchema):
    name: str | None = None
    manufacturer: str | None = None
    description: str | None = None
    price: int | None = None


class ProductSchema(ProductBaseSchema):
    id: int
