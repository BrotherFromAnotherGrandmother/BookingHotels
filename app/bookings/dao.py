from datetime import date

from fastapi import HTTPException
from sqlalchemy import select, and_, or_, func, insert, delete

from sqlalchemy.exc import SQLAlchemyError

from app.hotels.dao import HotelDAO
from app.hotels.models import Hotels
from app.users.dependencies import get_current_user

from app.dao.base import BaseDAO
from app.bookings.models import Bookings
from app.database import async_session_maker, engine
from app.exceptions import RoomFullyBooked
from app.hotels.rooms.models import Rooms
from loguru import logger

from app.users.models import Users


class BookingDAO(BaseDAO):
    model = Bookings

    @classmethod
    async def add(
            cls,
            user_id: int,
            room_id: int,
            date_from: date,
            date_to: date,
    ):
        """
        WITH booked_rooms AS (
            SELECT * FROM bookings
            WHERE room_id = 1 AND
                (date_from >= '2023-05-15' AND date_from <= '2023-06-20') OR
                (date_from <= '2023-05-15' AND date_to > '2023-05-15')
        )
        """
        try:
            async with async_session_maker() as session:
                booked_rooms = (
                    select(Bookings)
                    .where(
                        and_(
                            Bookings.room_id == room_id,
                            or_(
                                and_(
                                    Bookings.date_from >= date_from,
                                    Bookings.date_from <= date_to,
                                ),
                                and_(
                                    Bookings.date_from <= date_from,
                                    Bookings.date_to > date_from,
                                ),
                            ),
                        )
                    )
                    .cte("booked_rooms")
                )

                """""
                SELECT rooms.quantity - COUNT(booked_rooms.room_id) FROM rooms
                LEFT JOIN booked_rooms ON booked_rooms.room_id = rooms.id
                WHERE rooms.id = 1
                GROUP BY rooms.quantity, booked_rooms.room_id
                """""

                get_rooms_left = (
                    select(
                        (Rooms.quantity - func.count(booked_rooms.c.room_id).filter(
                            booked_rooms.c.room_id.is_not(None))).label(
                            "rooms_left"
                        )
                    )
                    .select_from(Rooms)
                    .join(booked_rooms, booked_rooms.c.room_id == Rooms.id, isouter=True)
                    .where(Rooms.id == room_id)
                    .group_by(Rooms.quantity, booked_rooms.c.room_id)
                )

                # Рекомендую выводить SQL запрос в консоль для сверки
                # logger.debug(get_rooms_left.compile(engine, compile_kwargs={"literal_binds": True}))

                rooms_left = await session.execute(get_rooms_left)
                rooms_left: int = rooms_left.scalar()

                if rooms_left > 0:
                    get_price = select(Rooms.price).filter_by(id=room_id)
                    price = await session.execute(get_price)
                    price: int = price.scalar()
                    add_booking = (
                        insert(Bookings)
                        .values(
                            room_id=room_id,
                            user_id=user_id,
                            date_from=date_from,
                            date_to=date_to,
                            price=price,
                        )
                        .returning(Bookings
                                   # Bookings.id,
                                   # Bookings.user_id,
                                   # Bookings.room_id,
                                   # Bookings.date_from,
                                   # Bookings.date_to,
                                   )
                    )

                    new_booking = await session.execute(add_booking)
                    await session.commit()
                    return new_booking.scalar()
                    # return new_booking.mappings().one()
                else:
                    raise RoomFullyBooked
        except RoomFullyBooked:
            raise RoomFullyBooked
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc: Cannot add booking"
            elif isinstance(e, Exception):
                msg = "Unknown Exc: Cannot add booking"
            extra = {
                "user_id": user_id,
                "room_id": room_id,
                "date_from": date_from,
                "date_to": date_to,
            }
            logger.error(msg, extra=extra, exc_info=True)

    @classmethod
    async def get_all_bookings_for_current_user(
            cls,
            user_id: int,
    ):
        async with async_session_maker() as session:
            all_information = (
                select(Bookings, Hotels.name, Hotels.image_id, Rooms.description, Hotels.services)
                .join(Rooms, Bookings.room_id == Rooms.id)
                .join(Hotels, Rooms.hotel_id == Hotels.id)
                .where(Bookings.user_id == user_id)
            )

            result = await session.execute(all_information)
            return result.mappings().all()

    @classmethod
    async def delete_booking_for_current_user(
            cls,
            booking_id: int,
            user_id: int,
    ):
        async with async_session_maker() as session:
            booking = await session.get(Bookings, booking_id)
            if booking.user_id == user_id:
                delete_booking = (
                    delete(Bookings)
                    .where(Bookings.user_id == user_id)
                    .where(Bookings.id == booking_id)
                )
                await session.execute(delete_booking)
                await session.commit()
            else:
                raise HTTPException(status_code=403, detail="You are not authorized to delete this booking.")
