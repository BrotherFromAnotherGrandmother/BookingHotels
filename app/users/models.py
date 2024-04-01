from sqlalchemy import Column, Integer, ForeignKey, Date, Computed, String, JSON
from sqlalchemy.orm import Mapped, mapped_column

from sqlalchemy.orm import relationship

from app.database import Base


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    email: Mapped[str] = mapped_column(nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)

    """Это relationship на модель Users, этим самым мы связываем эти две модели"""
    booking: Mapped[list["Bookings"]] = relationship(back_populates="user")

    """Указываем дандр-метод __str__ для красивого вида в админ-панели"""

    def __str__(self):
        return f"Пользователь: {self.email}"


