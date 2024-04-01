from datetime import date
from sqlalchemy import select, func, or_, and_

from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.hotels.models import Hotels
from app.hotels.rooms.models import Rooms


class HotelDAO(BaseDAO):
    model = Hotels

    @classmethod
    async def search_hotels_by_location_and_time(
            cls,
            location: str,
            data_from: date,
            data_to: date,

    ):
        async with async_session_maker() as session:
            get_all_hotels = (
                select(Hotels)
                .filter(
                    Hotels.location.like('%Алтай%'),
                    Hotels.rooms_quantity >= 1,

                )
            )

            result = await session.execute(get_all_hotels)
            hotels = result.scalars().all()

            for hotel in hotels:
                booked_rooms = (
                    select(func.count(Bookings.id))
                    .where(
                        Bookings.room_id == hotel.id,
                        or_(
                            and_(Bookings.date_from <= data_from, Bookings.date_to >= data_from),
                            and_(Bookings.date_from <= data_to, Bookings.date_to >= data_to),
                            and_(Bookings.date_from >= data_from, Bookings.date_to <= data_to),
                        )
                    )
                )
                booked_rooms_count = await session.execute(booked_rooms)
                hotel.available_rooms = hotel.rooms_quantity - booked_rooms_count.scalar()

            return hotels

    @classmethod
    async def get_specific_hotel(
            cls,
            hotel_id: int

    ):
        async with async_session_maker() as session:
            get_hotel_by_id = (
                select(Hotels)
                .where(Hotels.id == hotel_id)
            )

            result = await session.execute(get_hotel_by_id)
            return result.scalars().all()

# Room.date.between(check_in_date, check_out_date), Room.available > 0).all()

# async with async_session_maker() as session:
#     get_all_hotels = (
#         select(Hotels)
#         .where(
#             (Hotels.location.like('%Алтай%'))
#             .where(
#                 Hotels.rooms_quantity
#             )
#         )
#     )
