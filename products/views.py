from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud
from .schemas import ProductCreateSchema
from .schemas import ProductSchema
from .schemas import ProductUpdatePartialSchema
from auth.utils import get_current_user_name
from auth.utils import get_user_by_username
from core.models import db_helper
from core.models import User

router = APIRouter(tags=["Product"])


@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: ProductCreateSchema,
    session=Depends(db_helper.scoped_session_dependency),
    current_user_name: str = Depends(get_current_user_name),
):
    current_user: User | None = await get_user_by_username(
        session=session, username=current_user_name
    )
    if current_user.is_super_admin or current_user.is_admin:
        return await crud.create_product(session=session, product=product_in)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")


@router.get("/", response_model=list[ProductSchema])
async def get_products(
    session=Depends(db_helper.scoped_session_dependency),
):
    return await crud.get_products(session=session)


@router.get("/{product_id}", response_model=ProductSchema)
async def get_product(
    product_id: int,
    session=Depends(db_helper.scoped_session_dependency),
):
    product = await crud.get_product(session=session, product_id=product_id)
    if product:
        return product
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Product not found!"
    )


@router.patch("/{product_id}", response_model=ProductSchema)
async def update_product(
    product_update: ProductUpdatePartialSchema,
    product_id: int,
    session=Depends(db_helper.scoped_session_dependency),
    current_user_name: str = Depends(get_current_user_name),
):
    product_not_found_exc = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Product {product_id} not found!"
    )
    product = await crud.get_product(session=session, product_id=product_id)
    if product:
        current_user: User | None = await get_user_by_username(
            session=session, username=current_user_name
        )
        if current_user.is_super_admin or current_user.is_admin:
            return await crud.upgrade_product(
                session=session,
                product=product,
                product_update=product_update,
            )
        raise product_not_found_exc
    raise product_not_found_exc


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
    current_user_name: str = Depends(get_current_user_name),
):
    product_not_found_exc = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Product {product_id} not found!"
    )
    current_user: User | None = await get_user_by_username(
        session=session, username=current_user_name
    )
    if current_user.is_super_admin or current_user.is_admin:
        product = await crud.get_product(session=session, product_id=product_id)
        if product:
            await crud.delete_product(session=session, product=product)
            return None
        raise product_not_found_exc
    raise product_not_found_exc
