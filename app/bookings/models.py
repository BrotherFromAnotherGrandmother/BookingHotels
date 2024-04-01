import datetime

from sqlalchemy import ForeignKey, Date, Computed
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from sqlalchemy.orm import relationship


class Bookings(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    date_from: Mapped[datetime] = mapped_column(Date, nullable=False)
    date_to: Mapped[datetime] = mapped_column(Date, nullable=False)
    price: Mapped[int] = mapped_column(nullable=False)
    total_cost: Mapped[int] = mapped_column(Computed("(date_to - date_from) * price"))
    total_days: Mapped[int] = mapped_column(Computed("date_to - date_from"))

    """Это relationship на модель Bookings, этим самым мы связываем эти две модели"""
    user: Mapped[list["Users"]] = relationship(back_populates="booking")
    room: Mapped[list["Rooms"]] = relationship(back_populates="booking")

    """Указываем дандр-метод __str__ для красивого вида в админ-панели"""

    def __str__(self):
        return f"Бронь: #{self.id}"
