from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from .base import Base

if TYPE_CHECKING:
    from .cart_item import CartItem
    from .order import Order
    from .user import User


class Cart(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    order: Mapped["Order"] = relationship(back_populates="cart")
    items: Mapped[list["CartItem"]] = relationship(back_populates="cart")
    user: Mapped["User"] = relationship(back_populates="carts")

    @property
    def get_cost(self):
        cost: int = 0
        for item in self.items:
            cost += item.cost
        return cost
