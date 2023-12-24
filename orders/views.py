from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from . import crud
from .carts.views import router as cart_router
from .schemas import OrderCreateSchema
from .schemas import OrderSchema
from auth.utils import get_current_user_name
from auth.utils import get_user_by_username
from core.models import db_helper
from core.models import User

router = APIRouter(tags=["Order"])

router.include_router(cart_router, prefix="/cart")


@router.post("/", response_model=OrderSchema, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_in: OrderCreateSchema,
    current_user_name: str = Depends(get_current_user_name),
    session=Depends(db_helper.scoped_session_dependency),
):
    current_user: User | None = await get_user_by_username(
        session=session, username=current_user_name
    )
    if current_user:
        return await crud.create_order(
            session=session, order=order_in, user_id=current_user.id
        )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="You need to log in"
    )


@router.get("/", response_model=list[OrderSchema])
async def get_orders(
    current_user_name: str = Depends(get_current_user_name),
    session=Depends(db_helper.scoped_session_dependency),
):
    current_user: User | None = await get_user_by_username(
        session=session, username=current_user_name
    )
    if current_user.is_super_admin or current_user.is_admin:
        return await crud.get_orders(session=session)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


@router.get("/{order_id}", response_model=OrderSchema)
async def get_order(
    order_id: int,
    current_user_name: str = Depends(get_current_user_name),
    session=Depends(db_helper.scoped_session_dependency),
):
    if current_user_name:
        order = await crud.get_order_by_id(session=session, order_id=order_id)
        if order:
            return order
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Order {order_id} not found!"
        )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="You need to log in"
    )
