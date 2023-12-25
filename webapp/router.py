from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from .auth.router import router as auth_router
from .forms import CartItemUpdateForm
from .order.router import router as order_router
from auth.utils import get_current_user_name
from auth.utils import get_user_by_username
from core.models import db_helper
from core.models import User
from orders.crud import create_cart
from orders.crud import create_cart_item_with_one_product
from orders.crud import delete_cart_item
from orders.crud import get_card_by_user_id
from orders.crud import get_cart_item_by_id
from orders.crud import get_cart_items_by_cart_id
from orders.crud import update_cart_item
from orders.schemas import CartItemUpdateSchema
from products.crud import get_product
from products.crud import get_product_by_name
from products.crud import get_products

router = APIRouter(tags=["Webapp"])
router.include_router(auth_router, prefix="/auth")
router.include_router(order_router, prefix="/order")

templates = Jinja2Templates(directory="templates")


@router.get("/")
async def product_list(
    request: Request,
    session=Depends(db_helper.scoped_session_dependency),
):
    products = await get_products(session=session)
    return templates.TemplateResponse(
        "product_list.html",
        {"request": request, "products": products},
    )


@router.get("/product/{product_name}", response_class=HTMLResponse)
async def product_detail(
    request: Request,
    product_name: str,
    session=Depends(db_helper.scoped_session_dependency),
):
    product = await get_product_by_name(session=session, product_name=product_name)
    if product:
        return templates.TemplateResponse(
            "product_detail.html", {"request": request, "product": product}
        )
    return templates.TemplateResponse(
        name="404.html",
        context={"request": request},
        status_code=status.HTTP_404_NOT_FOUND,
    )


@router.get("/cart", response_class=HTMLResponse)
async def get_cart(
    request: Request,
    session=Depends(db_helper.scoped_session_dependency),
    current_user_name: str = Depends(get_current_user_name),
):
    current_user: User | None = await get_user_by_username(
        session=session, username=current_user_name
    )
    cart = await get_card_by_user_id(session=session, user_id=current_user.id)
    if not cart:
        cart = await create_cart(session=session, user_id=current_user.id)
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
        "cart.html",
        {
            "request": request,
            "cart": cart,
            "current_user_name": current_user_name,
            "products": products,
            "total_cost": total_cost,
        },
    )


@router.get("/cart/{product_id}", response_class=HTMLResponse)
async def get_cart(
    request: Request,
    product_id: int,
    session=Depends(db_helper.scoped_session_dependency),
    current_user_name: str = Depends(get_current_user_name),
):
    current_user: User | None = await get_user_by_username(
        session=session, username=current_user_name
    )
    cart = await get_card_by_user_id(session=session, user_id=current_user.id)
    if not cart:
        cart = await create_cart(session=session, user_id=current_user.id)
    try:
        await create_cart_item_with_one_product(
            session=session, cart_id=cart.id, product_id=product_id
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
            "cart.html",
            {
                "request": request,
                "cart": cart,
                "current_user_name": current_user_name,
                "products": products,
                "total_cost": total_cost,
            },
        )
    except HTTPException:
        return templates.TemplateResponse(
            name="404.html",
            context={"request": request},
            status_code=status.HTTP_404_NOT_FOUND,
        )


@router.get("/update_cart/", response_class=HTMLResponse)
async def update_cart(
    request: Request,
    session=Depends(db_helper.scoped_session_dependency),
    current_user_name: str = Depends(get_current_user_name),
):
    current_user: User | None = await get_user_by_username(
        session=session, username=current_user_name
    )
    cart = await get_card_by_user_id(session=session, user_id=current_user.id)
    items = await get_cart_items_by_cart_id(session=session, cart_id=cart.id)
    products = []
    for item in items:
        product = await get_product(session=session, product_id=item.product_id)
        products.append({product.name: [item.quantity]})
    return templates.TemplateResponse(
        "update_cart.html", {"request": request, "products": products}
    )


@router.post("/update_cart/", response_class=HTMLResponse)
async def update_cart(
    request: Request,
    session=Depends(db_helper.scoped_session_dependency),
    current_user_name: str = Depends(get_current_user_name),
):
    current_user: User | None = await get_user_by_username(
        session=session, username=current_user_name
    )
    cart = await get_card_by_user_id(session=session, user_id=current_user.id)
    items = await get_cart_items_by_cart_id(session=session, cart_id=cart.id)
    products = []
    for item in items:
        product = await get_product(session=session, product_id=item.product_id)
        form = CartItemUpdateForm(request=request)
        await form.load_data()
        quantity = item.quantity
        new_quantity = (
            form.quantity
            if (form.quantity and int(form.quantity) > 0)
            else item.quantity
        )
        products.append({product.name: [quantity, new_quantity]})
        await update_cart_item(
            session=session,
            cart_item=item,
            cart_item_update=CartItemUpdateSchema(quantity=new_quantity),
        )
    return templates.TemplateResponse(
        "update_cart.html", {"request": request, "products": products}
    )


@router.get("/delete_cart_item/{cart_item_id}", response_class=HTMLResponse)
async def delete_cart_item_by_id(
    request: Request,
    cart_item_id: int,
    session=Depends(db_helper.scoped_session_dependency),
    current_user_name: str = Depends(get_current_user_name),
):
    if current_user_name:
        cart_item = await get_cart_item_by_id(
            session=session, cart_item_id=cart_item_id
        )
        if cart_item:
            await delete_cart_item(session=session, cart_item=cart_item)
            redirect_url = request.url_for("get_cart")
            return RedirectResponse(redirect_url)
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


@router.get("/clear_cart", response_class=HTMLResponse)
async def clear_cart(
    request: Request,
    session=Depends(db_helper.scoped_session_dependency),
    current_user_name: str = Depends(get_current_user_name),
):
    current_user: User | None = await get_user_by_username(
        session=session, username=current_user_name
    )
    cart = await get_card_by_user_id(session=session, user_id=current_user.id)
    items = await get_cart_items_by_cart_id(session=session, cart_id=cart.id)
    for item in items:
        await delete_cart_item(session=session, cart_item=item)
    redirect_url = request.url_for("get_cart")
    return RedirectResponse(redirect_url)
