from typing import List

from fastapi import Request
from pydantic import EmailStr


class OrderCreateForm:
    def __init__(self, request: Request):
        self.request = request
        self.errors: List = []
        self.first_name: str | None = None
        self.last_name: str | None = None
        self.email: EmailStr | None = None
        self.address: str | None = None
        self.postal_code: str | None = None
        self.city: str | None = None

    async def load_data(self):
        form = await self.request.form()
        self.first_name = form.get("first_name")
        self.last_name = form.get("last_name")
        self.email = form.get("email")
        self.address = form.get("address")
        self.postal_code = form.get("postal_code")
        self.city = form.get("city")

    async def is_valid(self) -> bool:
        if not self.first_name:
            self.errors.append("First name is required")
        if not self.last_name:
            self.errors.append("Last name is required")
        if not self.email:
            self.errors.append("Email is required")
        if not self.address:
            self.errors.append("Address is required")
        if not self.postal_code:
            self.errors.append("Postal code is required")
        if not self.city:
            self.errors.append("City is required")
        if not self.errors:
            return True
        return False
