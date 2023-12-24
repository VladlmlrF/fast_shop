from pydantic import BaseModel
from pydantic import EmailStr


class CartItemBaseSchema(BaseModel):
    product_id: int
    quantity: int


class CartItemCreateSchema(CartItemBaseSchema):
    pass


class CartItemUpdateSchema(BaseModel):
    quantity: int | None = None


class CartItemSchema(CartItemBaseSchema):
    cart_id: int
    id: int


class CartBaseSchema(BaseModel):
    user_id: int


class CartCreateSchema(CartBaseSchema):
    pass


class CartUpdateSchema(CartBaseSchema):
    pass


class CartSchema(CartBaseSchema):
    id: int


class OrderBaseSchema(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    address: str
    postal_code: int
    city: str
    discount: int


class OrderCreateSchema(OrderBaseSchema):
    cart_id: int


class OrderUpdateSchema(OrderBaseSchema):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    address: str | None = None
    postal_code: int | None = None
    city: str | None = None
    coupon_id: int | None = None
    discount: int | None = None


class OrderSchema(OrderBaseSchema):
    id: int
    user_id: int
    cart_id: int
