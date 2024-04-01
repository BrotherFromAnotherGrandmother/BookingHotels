from datetime import date

from fastapi import APIRouter, Request, Depends, BackgroundTasks
from pydantic import TypeAdapter, parse_obj_as

from app.bookings.dao import BookingDAO
from app.bookings.service import BookingService
from app.exceptions import RoomCannotBeBooked, UserIsNotPresentException
from app.hotels.rooms.models import Rooms
from app.bookings.schemas import SchemasBooking, SNewBooking
from app.tasks.celery_app import celery_worker
from app.tasks.tasks import send_booking_confirmation_email
from app.users.dependencies import get_current_user
from app.users.models import Users

from celery.result import AsyncResult

router = APIRouter(
    prefix="/bookings",
    tags=["Бронирование"]
)


@router.post("", status_code=201)
async def add_booking(
        room_id: int,
        data_from: date,
        date_to: date,
        booking: SNewBooking,
        background_tasks: BackgroundTasks,
        user: Users = Depends(get_current_user),
):
    # new_booking = await BookingService.add_booking(
    #     booking,
    #     background_tasks,
    #     user,
    # )
    # return new_booking

    booking = await BookingDAO.add(user.id, room_id, data_from, date_to)
    booking_dict = parse_obj_as(SchemasBooking, booking).dict()

    send_booking_confirmation_email.delay(booking_dict, user.email)
    return booking_dict


@router.get("", status_code=200)
async def get_bookings_current_user(
        current_user: Users = Depends(get_current_user),
):
    if current_user:
        get_bookings = await BookingDAO.get_all_bookings_for_current_user(current_user.id)
        return get_bookings


@router.delete("", status_code=204)
async def delete_booking(
        booking_id: int,
        current_user: Users = Depends(get_current_user),
):
    if current_user:
        delete = await BookingDAO.delete_booking_for_current_user(booking_id, current_user.id)
        return delete
    raise UserIsNotPresentException
