from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import responses
from fastapi import status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from .forms import OrderCreateForm
from auth.utils import get_current_user_name
from auth.utils import get_user_by_username
from core.models import db_helper
from core.models import User
from orders import crud
from orders.crud import get_card_by_user_id
from orders.crud import get_cart_items_by_cart_id
from orders.schemas import OrderCreateSchema
from products.crud import get_product

router = APIRouter(tags=["Order"])

templates = Jinja2Templates(directory="templates")


@router.get("/create", response_class=HTMLResponse)
async def order(
    request: Request,
    current_user_name: str = Depends(get_current_user_name),
):
    if current_user_name:
        return templates.TemplateResponse("order_create.html", {"request": request})
    return templates.TemplateResponse(
        name="404.html",
        context={"request": request},
        status_code=status.HTTP_404_NOT_FOUND,
    )


@router.post("/create", response_class=HTMLResponse)
async def order(
    request: Request,
    session=Depends(db_helper.scoped_session_dependency),
    current_user_name: str = Depends(get_current_user_name),
):
    form = OrderCreateForm(request=request)
    current_user: User | None = await get_user_by_username(
        session=session, username=current_user_name
    )
    await form.load_data()
    if await form.is_valid():
        cart = await crud.get_card_by_user_id(session=session, user_id=current_user.id)
        new_order = OrderCreateSchema(
            first_name=form.first_name,
            last_name=form.last_name,
            email=form.email,
            address=form.address,
            postal_code=int(form.postal_code),
            city=form.city,
            discount=0,
            cart_id=cart.id,
        )
        try:
            current_order = await crud.create_order(
                session=session, order=new_order, user_id=current_user.id
            )
            form.__dict__.update(msg="Order successfully placed")
            # return templates.TemplateResponse("order_create.html", form.__dict__)
            return responses.RedirectResponse(
                url=f"/shop/order/{current_order.id}?msg={form.__dict__.get('msg')}",
                status_code=status.HTTP_302_FOUND,
            )
        except HTTPException:
            form.__dict__.update(msg="")
            return templates.TemplateResponse("order_create.html", form.__dict__)
    form.__dict__.get("errors").append("Incorrect data entered")
    return templates.TemplateResponse("order_create.html", form.__dict__)


@router.get("/{order_id}", response_class=HTMLResponse)
async def show_order(
    request: Request,
    order_id: int,
    session=Depends(db_helper.scoped_session_dependency),
    current_user_name: str = Depends(get_current_user_name),
):
    if current_user_name:
        current_order = await crud.get_order_by_id(session=session, order_id=order_id)
        if current_order:
            cart = await get_card_by_user_id(
                session=session, user_id=current_order.user_id
            )
            items = await get_cart_items_by_cart_id(session=session, cart_id=cart.id)
            products = []
            total_cost: int = 0
            for item in items:
                product = await get_product(session=session, product_id=item.product_id)
                item_id: int = item.id
                quantity: int = item.quantity
                products.append({product: [quantity, item_id]})
                item_cost = product.price * quantity
                total_cost += item_cost
            return templates.TemplateResponse(
                "order.html",
                {
                    "request": request,
                    "order": current_order,
                    "products": products,
                    "total_cost": total_cost,
                },
            )
        return templates.TemplateResponse(
            name="404.html",
            context={"request": request},
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return templates.TemplateResponse(
        name="404.html",
        context={"request": request},
        status_code=status.HTTP_404_NOT_FOUND,
    )
