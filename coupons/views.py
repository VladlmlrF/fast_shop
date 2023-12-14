from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud
from .schemas import CouponCreateSchema
from .schemas import CouponSchema
from .schemas import CouponUpdateSchema
from auth.utils import get_current_user_name
from auth.utils import get_user_by_username
from core.models import db_helper
from core.models import User

router = APIRouter(tags=["Coupon"])


@router.post("/", response_model=CouponSchema, status_code=status.HTTP_201_CREATED)
async def create_coupon(
    coupon_in: CouponCreateSchema,
    session=Depends(db_helper.scoped_session_dependency),
    current_user_name: str = Depends(get_current_user_name),
):
    current_user: User | None = await get_user_by_username(
        session=session, username=current_user_name
    )
    if current_user.is_super_admin or current_user.is_admin:
        return await crud.create_coupon(session=session, coupon=coupon_in)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")


@router.get("/", response_model=list[CouponSchema])
async def get_coupons(
    session=Depends(db_helper.scoped_session_dependency),
):
    return await crud.get_coupons(session=session)


@router.get("/{coupon_id}", response_model=CouponSchema)
async def get_coupon(
    coupon_id: int,
    session=Depends(db_helper.scoped_session_dependency),
):
    coupon = await crud.get_coupon(session=session, coupon_id=coupon_id)
    if coupon:
        return coupon
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Coupon not found!"
    )


@router.patch("/{coupon_id}", response_model=CouponSchema)
async def update_coupon(
    coupon_update: CouponUpdateSchema,
    coupon_id: int,
    session=Depends(db_helper.scoped_session_dependency),
    current_user_name: str = Depends(get_current_user_name),
):
    coupon_not_found_exc = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Coupon {coupon_id} not found!"
    )
    coupon = await crud.get_coupon(session=session, coupon_id=coupon_id)
    if coupon:
        current_user: User | None = await get_user_by_username(
            session=session, username=current_user_name
        )
        if current_user.is_super_admin or current_user.is_admin:
            return await crud.upgrade_coupon(
                session=session,
                coupon=coupon,
                coupon_update=coupon_update,
            )
        raise coupon_not_found_exc
    raise coupon_not_found_exc


@router.delete("/{coupon_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_coupon(
    coupon_id: int,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
    current_user_name: str = Depends(get_current_user_name),
):
    coupon_not_found_exc = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Product {coupon_id} not found!"
    )
    current_user: User | None = await get_user_by_username(
        session=session, username=current_user_name
    )
    if current_user.is_super_admin or current_user.is_admin:
        coupon = await crud.get_coupon(session=session, coupon_id=coupon_id)
        if coupon:
            await crud.delete_coupon(session=session, coupon=coupon)
            return None
        raise coupon_not_found_exc
    raise coupon_not_found_exc
