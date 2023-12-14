from fastapi import HTTPException
from fastapi import status
from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import ProductCreateSchema
from .schemas import ProductUpdatePartialSchema
from core.models import Product


async def create_product(session: AsyncSession, product: ProductCreateSchema):
    """Create new product"""
    new_product = Product(
        name=product.name,
        manufacturer=product.manufacturer,
        description=product.description,
        price=product.price,
    )
    try:
        session.add(new_product)
        await session.commit()
        return new_product
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Product with that name already exists!",
        )


async def get_products(session: AsyncSession) -> list[Product]:
    """Get all products"""
    statement = select(Product).order_by(Product.name)
    result: Result = await session.execute(statement=statement)
    products = result.scalars().all()
    return list(products)


async def get_product(session: AsyncSession, product_id: int) -> Product | None:
    """Get product by id"""
    return await session.get(Product, product_id)


async def upgrade_product(
    session: AsyncSession,
    product: Product,
    product_update: ProductUpdatePartialSchema,
):
    """Update product"""
    for key, value in product_update.model_dump(exclude_unset=True).items():
        setattr(product, key, value)
    await session.commit()
    return product


async def delete_product(session: AsyncSession, product: Product):
    """Delete product"""
    await session.delete(product)
    await session.commit()
