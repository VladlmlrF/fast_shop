from typing import List

from fastapi import Request
from pydantic import EmailStr


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.username: str | None = None
        self.password: str | None = None

    async def load_data(self):
        form = await self.request.form()
        self.username = form.get("username")
        self.password = form.get("password")

    async def is_valid(self) -> bool:
        if not self.username:
            self.errors.append("Username is required")
        if not self.password:
            self.errors.append("Password is required")
        if not self.errors:
            return True
        return False


class UserCreateForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.username: str | None = None
        self.email: EmailStr | None = None
        self.password: str | None = None

    async def load_data(self):
        form = await self.request.form()
        self.username = form.get("username")
        self.email = form.get("email")
        self.password = form.get("password")

    async def is_valid(self):
        if not self.username or not len(self.username) > 3:
            self.errors.append("Username should be > 3 chars")
        if not self.email:
            self.errors.append("Email is required")
        if not self.errors:
            return True
        return False
