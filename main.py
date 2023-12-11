import uvicorn
from fastapi import FastAPI

from auth.views import router as auth_router
from users.views import router as user_router

app = FastAPI(title="Fast Shop")


app.include_router(user_router, prefix="/users")
app.include_router(auth_router, prefix="/auth")


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
