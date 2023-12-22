from fastapi import HTTPException
from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Cart
from core.models import CartItem
from orders.schemas import CartItemCreateSchema
from orders.schemas import CartItemUpdateSchema
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


async def get_cart_item_by_cart_id_and_product_id(
    session: AsyncSession,
    cart_id: int,
    product_id: int,
):
    """Get cart_item by cart.id and product.id"""
    statement = (
        select(CartItem)
        .where(CartItem.cart_id == cart_id)
        .where(CartItem.product_id == product_id)
    )
    cart_item: CartItem | None = await session.scalar(statement)
    return cart_item


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
    old_cart_item = await get_cart_item_by_cart_id_and_product_id(
        session=session, cart_id=cart_id, product_id=cart_item.product_id
    )
    if old_cart_item:
        old_cart_item.quantity += cart_item.quantity
        await session.commit()
        return old_cart_item

    new_cart_item = CartItem(
        cart_id=cart_id,
        product_id=cart_item.product_id,
        price=price,
        quantity=cart_item.quantity,
    )
    session.add(new_cart_item)
    await session.commit()
    return new_cart_item


async def create_cart_item_with_one_product(
    session: AsyncSession, cart_id: int, product_id: int, quantity: int = 1
):
    """Create cart_item"""
    product = await get_product(session=session, product_id=product_id)
    if product:
        price = product.price
        old_cart_item = await get_cart_item_by_cart_id_and_product_id(
            session=session, cart_id=cart_id, product_id=product_id
        )
        if old_cart_item:
            old_cart_item.quantity += quantity
            await session.commit()
            return old_cart_item

        new_cart_item = CartItem(
            cart_id=cart_id,
            product_id=product_id,
            price=price,
            quantity=quantity,
        )
        session.add(new_cart_item)
        await session.commit()
        return new_cart_item
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail=f"Product {product_id} not found"
    )


async def get_cart_items_by_cart_id(
    session: AsyncSession,
    cart_id: int,
):
    """Get cart items by cart.id"""
    statement = select(CartItem).where(CartItem.cart_id == cart_id)
    items: list[CartItem] = list(await session.scalars(statement))
    return items


async def get_cart_item_by_id(
    session: AsyncSession,
    cart_item_id: int,
):
    """Get cart_item by user_id"""
    statement = select(CartItem).where(CartItem.id == cart_item_id)
    cart_item: CartItem | None = await session.scalar(statement=statement)
    return cart_item


async def update_cart_item(
    session: AsyncSession,
    cart_item: CartItem,
    cart_item_update: CartItemUpdateSchema,
) -> CartItem:
    """Update cart_item"""
    for name, value in cart_item_update.model_dump(exclude_unset=False).items():
        setattr(cart_item, name, value)
    await session.commit()
    return cart_item
