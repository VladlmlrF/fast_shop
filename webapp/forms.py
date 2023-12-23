from fastapi import Request


class CartItemUpdateForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.quantity: int | None = None

    async def load_data(self):
        form = await self.request.form()
        self.quantity = form.get("quantity")
