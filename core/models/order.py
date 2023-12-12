from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from .base import Base

if TYPE_CHECKING:
    from .coupon import Coupon
    from .order_item import OrderItem


class Order(Base):
    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str]
    address: Mapped[str]
    postal_code: Mapped[int]
    city: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    paid: Mapped[bool] = mapped_column(default=False)
    coupon_id: Mapped[int] = mapped_column(ForeignKey("coupons.id"))
    discount: Mapped[int] = mapped_column(default=0, server_default="0")

    coupon: Mapped["Coupon"] = relationship(back_populates="orders")
    order_items: Mapped["OrderItem"] = relationship(back_populates="order_items")

    @property
    def get_total_cost_before_discount(self):
        return sum(order_item.get_cost for order_item in self.order_items.all())

    @property
    def get_discount(self):
        total_cost = self.get_total_cost_before_discount
        return int(total_cost * (self.discount / 100))

    @property
    def get_total_cost(self):
        total_cost = self.get_total_cost_before_discount
        return total_cost - self.get_discount
