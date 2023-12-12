from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from .base import Base

if TYPE_CHECKING:
    from .order_item import OrderItem


class Product(Base):
    name: Mapped[str]
    manufacturer: Mapped[str]
    description: Mapped[str]
    price: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    orders_details: Mapped[list["OrderItem"]] = relationship(back_populates="product")
