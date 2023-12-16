import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from auth.views import router as auth_router
from coupons.views import router as coupon_router
from orders.views import router as order_router
from products.views import router as product_router
from shop.router import router as shop_router
from users.views import router as user_router

app = FastAPI(title="Fast Shop")

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static", html=True), name="static")

origins = [
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "PATCH"],
    allow_headers=[
        "Content-Type",
        "Set-Cookie",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Origin",
        "Authorization",
    ],
)


@app.get("/", response_class=HTMLResponse)
async def home_page():
    return RedirectResponse("/shop")


app.include_router(user_router, prefix="/users")
app.include_router(auth_router, prefix="/auth")
app.include_router(product_router, prefix="/products")
app.include_router(coupon_router, prefix="/coupons")
app.include_router(order_router, prefix="/order")
app.include_router(shop_router, prefix="/shop")


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
