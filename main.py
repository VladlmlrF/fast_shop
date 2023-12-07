import uvicorn
from fastapi import FastAPI

from users.views import router as user_router

app = FastAPI(title="Fast Shop")


app.include_router(user_router, prefix="/users")


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
