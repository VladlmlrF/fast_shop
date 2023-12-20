from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from .base import Base

if TYPE_CHECKING:
    from .order import Order
    from .order import Cart


class Role(str, Enum):
    ORDINARY_USER = "ORDINARY_USER"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"


class User(Base):
    username: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    hashed_password: Mapped[str]
    role: Mapped[Role] = mapped_column(String, default=Role.ORDINARY_USER)

    orders: Mapped[list["Order"]] = relationship(back_populates="user")
    cart: Mapped["Cart"] = relationship(back_populates="user")

    @property
    def is_super_admin(self) -> bool:
        return Role.SUPER_ADMIN == self.role

    @property
    def is_admin(self) -> bool:
        return Role.ADMIN == self.role
