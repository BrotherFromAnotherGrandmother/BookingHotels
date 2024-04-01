from datetime import date

from sqlalchemy import select, func, or_, and_

from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.hotels.rooms.models import Rooms


class RoomDAO(BaseDAO):
    model = Rooms

    @classmethod
    async def search_for_rooms(
            cls,
            hotel_id: int,
            date_from: date,
            date_to: date,
    ):
        async with async_session_maker() as session:
            get_rooms_by_hotel_id = (
                select(Rooms)
                .where(Rooms.hotel_id == hotel_id)
            )
            result = await session.execute(get_rooms_by_hotel_id)
            rooms = result.scalars().all()

            for room in rooms:
                booked_rooms = (
                    select(func.count(Bookings.id))
                    .where(
                        Bookings.room_id == room.id,
                        or_(
                            and_(Bookings.date_from <= date_from, Bookings.date_to >= date_from),
                            and_(Bookings.date_from <= date_to, Bookings.date_to >= date_to),
                            and_(Bookings.date_from >= date_from, Bookings.date_to <= date_to),
                        )
                    )
                )
                booked_rooms_count = await session.execute(booked_rooms)
                room.available_rooms = room.quantity - booked_rooms_count.scalar()
                room.total_cost = room.price * (date_to - date_from).days

            return rooms
