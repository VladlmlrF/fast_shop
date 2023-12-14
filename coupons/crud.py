from fastapi import HTTPException
from fastapi import status
from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import CouponCreateSchema
from .schemas import CouponUpdateSchema
from core.models import Coupon


async def create_coupon(session: AsyncSession, coupon: CouponCreateSchema):
    """Create new coupon"""
    new_coupon = Coupon(
        code=coupon.code,
        valid_from=coupon.valid_from,
        valid_to=coupon.valid_to,
        discount=coupon.discount,
        active=coupon.active,
    )
    try:
        session.add(new_coupon)
        await session.commit()
        return new_coupon
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Coupon with code name already exists!",
        )


async def get_coupons(session: AsyncSession) -> list[Coupon]:
    """Get all coupons"""
    statement = select(Coupon).order_by(Coupon.id)
    result: Result = await session.execute(statement=statement)
    coupons = result.scalars().all()
    return list(coupons)


async def get_coupon(session: AsyncSession, coupon_id: int) -> Coupon | None:
    """Get coupon by id"""
    return await session.get(Coupon, coupon_id)


async def upgrade_coupon(
    session: AsyncSession,
    coupon: Coupon,
    coupon_update: CouponUpdateSchema,
):
    """Update coupon"""
    for key, value in coupon_update.model_dump(exclude_unset=True).items():
        setattr(coupon, key, value)
    await session.commit()
    return coupon


async def delete_coupon(session: AsyncSession, coupon: Coupon):
    """Delete coupon"""
    await session.delete(coupon)
    await session.commit()
