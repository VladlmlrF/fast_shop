from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi import status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from core.models import db_helper
from products.crud import get_product_by_name
from products.crud import get_products

# from auth.utils import get_current_user_name
# from auth.utils import get_user_by_username
# from core.models import User
# from orders.crud import create_cart

router = APIRouter(tags=["Pages"])

templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def product_list(
    request: Request,
    session=Depends(db_helper.scoped_session_dependency),
):
    products = await get_products(session=session)
    return templates.TemplateResponse(
        "product_list.html",
        {"request": request, "products": products},
    )


@router.get("/{product_name}", response_class=HTMLResponse)
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


# @router.get("/cart", response_model=HTMLResponse)
# async def get_cart(
#     request: Request,
#     product_name: str,
#     session=Depends(db_helper.scoped_session_dependency),
#     current_user_name: str = Depends(get_current_user_name),
# ):
#     current_user: User | None = await get_user_by_username(
#         session=session, username=current_user_name
#     )
#     cart = create_cart(session=session, user_id=current_user.id)
