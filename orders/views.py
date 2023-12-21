from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from . import crud
from .schemas import CartItemCreateSchema
from .schemas import CartSchema
from auth.utils import get_current_user_name
from auth.utils import get_user_by_username
from core.models import db_helper
from core.models import User

router = APIRouter(tags=["Order"])


@router.post("/", response_model=CartSchema, status_code=status.HTTP_201_CREATED)
async def create_cart(
    current_user_name: str = Depends(get_current_user_name),
    session=Depends(db_helper.scoped_session_dependency),
):
    current_user: User | None = await get_user_by_username(
        session=session, username=current_user_name
    )
    return await crud.create_cart(session=session, user_id=current_user.id)


@router.get("/{cart_id}", response_model=CartSchema)
async def get_cart(
    cart_id: int,
    session=Depends(db_helper.scoped_session_dependency),
    current_user_name: str = Depends(get_current_user_name),
):
    if current_user_name:
        cart = await crud.get_cart(session=session, cart_id=cart_id)
        if cart:
            return cart
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Cart {cart_id} not found!"
        )
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Not authenticated"
    )


@router.patch("/{cart_id}", response_model=CartSchema)
async def cart_add_item(
    cart_item: CartItemCreateSchema,
    cart_id: int,
    session=Depends(db_helper.scoped_session_dependency),
    current_user_name: str = Depends(get_current_user_name),
):
    cart_not_found_exc = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Cart {cart_id} not found!"
    )
    if current_user_name:
        cart = await crud.get_cart(session=session, cart_id=cart_id)
        if cart:
            await crud.create_cart_item(
                session=session, cart_id=cart_id, cart_item=cart_item
            )
            return cart
        raise cart_not_found_exc
    raise cart_not_found_exc
