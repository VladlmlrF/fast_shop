from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from .base import Base

if TYPE_CHECKING:
    from .cart_item import CartItem


class Product(Base):
    name: Mapped[str] = mapped_column(unique=True)
    manufacturer: Mapped[str]
    description: Mapped[str]
    price: Mapped[int]
    available: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    cart_items: Mapped[list["CartItem"]] = relationship(back_populates="product")
