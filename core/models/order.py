from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from .base import Base

if TYPE_CHECKING:
    from .coupon import Coupon
    from .cart import Cart
    from .user import User


class Order(Base):
    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str]
    address: Mapped[str]
    postal_code: Mapped[int]
    city: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    paid: Mapped[bool] = mapped_column(default=False)
    coupon_id: Mapped[int | None] = mapped_column(
        ForeignKey("coupons.id"), default=None
    )
    discount: Mapped[int] = mapped_column(default=0, server_default="0")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    cart_id: Mapped[int] = mapped_column((ForeignKey("carts.id")))

    coupon: Mapped["Coupon"] = relationship(back_populates="orders")
    user: Mapped["User"] = relationship(back_populates="orders")
    cart: Mapped["Cart"] = relationship(back_populates="order")

    @property
    def get_total_cost_before_discount(self):
        return self.cart.get_cost

    @property
    def get_discount(self):
        total_cost = self.get_total_cost_before_discount
        return int(total_cost * (self.discount / 100))

    @property
    def get_total_cost(self):
        total_cost = self.get_total_cost_before_discount
        return total_cost - self.get_discount
