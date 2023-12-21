from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import responses
from fastapi import status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError

from .forms import LoginForm
from .forms import UserCreateForm
from auth.utils import authenticate_user
from auth.views import login_for_access_token
from core.models import db_helper
from users.crud import create_user
from users.schemas import UserCreateSchema

router = APIRouter(tags=["Auth"])

templates = Jinja2Templates(directory="templates")


@router.get("/register", response_class=HTMLResponse)
async def register(
    request: Request,
):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register", response_class=HTMLResponse)
async def register(
    request: Request,
    session=Depends(db_helper.scoped_session_dependency),
):
    form = UserCreateForm(request=request)
    await form.load_data()
    if await form.is_valid():
        user = UserCreateSchema(
            username=form.username, email=form.email, password=form.password
        )
        try:
            await create_user(session=session, user=user)
            return responses.RedirectResponse(
                url="/shop/auth/login?msg=You have been successfully registered! Log in to your account.",
                status_code=status.HTTP_302_FOUND,
            )
        except IntegrityError:
            form.__dict__.get("errors").append("Duplicate username or email")
            return templates.TemplateResponse("register.html", form.__dict__)
    return templates.TemplateResponse("register.html", form.__dict__)


@router.get("/login", response_class=HTMLResponse)
async def login(request: Request, msg: str | None = None):
    return templates.TemplateResponse("login.html", {"request": request, "msg": msg})


@router.post("/login")
async def login(
    request: Request,
    session=Depends(db_helper.scoped_session_dependency),
):
    form = LoginForm(request=request)
    await form.load_data()
    if await form.is_valid():
        try:
            await authenticate_user(
                session=session, username=form.username, password=form.password
            )
            form.__dict__.update(msg="Login Successful!")
            form.__dict__.update(success=True)
            response = templates.TemplateResponse("login.html", form.__dict__)
            await login_for_access_token(
                response=response, form_data=form, session=session
            )
            return response
        except HTTPException:
            form.__dict__.update(msg="")
            form.__dict__.get("errors").append("Incorrect username or Password")
            return templates.TemplateResponse("login.html", form.__dict__)
    form.__dict__.update(success=False)
    return templates.TemplateResponse("login.html", form.__dict__)
