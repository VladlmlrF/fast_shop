from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Cart
from core.models import CartItem
from orders.schemas import CartItemCreateSchema
from products.crud import get_product


async def create_cart(session: AsyncSession, user_id: int) -> Cart | None:
    """Create cart"""
    cart = Cart(user_id=user_id)
    session.add(cart)
    await session.commit()
    return cart


async def get_cart(session: AsyncSession, cart_id: int) -> Cart | None:
    """Get cart by id"""
    return await session.get(Cart, cart_id)


async def get_card_by_user_id(session: AsyncSession, user_id: int) -> Cart | None:
    """Get cart by user.id"""
    statement = select(Cart).where(Cart.user_id == user_id)
    cart: Cart | None = await session.scalar(statement)
    return cart


async def create_cart_item(
    session: AsyncSession,
    cart_id: int,
    cart_item: CartItemCreateSchema,
):
    """Create cart_item"""
    product = await get_product(session=session, product_id=cart_item.product_id)
    if product:
        price = product.price
    else:
        price = 0

    new_cart_item = CartItem(
        cart_id=cart_id,
        product_id=cart_item.product_id,
        price=price,
        quantity=cart_item.quantity,
    )
    session.add(new_cart_item)
    await session.commit()
    return new_cart_item
