from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from .base import Base

if TYPE_CHECKING:
    from .order import Order


class Coupon(Base):
    code: Mapped[str] = mapped_column(String(50), unique=True)
    valid_from: Mapped[datetime]
    valid_to: Mapped[datetime]
    discount: Mapped[int]
    active: Mapped[bool]

    orders: Mapped["Order"] = relationship(back_populates="coupon")
