from fastapi import BackgroundTasks
from pydantic import TypeAdapter

from app.bookings.dao import BookingDAO
from app.bookings.schemas import SNewBooking
from app.exceptions import RoomCannotBeBooked
from app.users.models import Users


class BookingService:
    """Мы выносим большую часть логики в service, потому что эта логика была привязана к нашему фреймворку FastAPI

    Пример как было:
    @router.post("", status_code=201)
    async def add_booking(
        booking: SNewBooking,
        background_tasks: BackgroundTasks,
        user: Users = Depends(get_current_user),
    ):
        и тут идет вся логика, которую мы вынесли

    Но если мы работаем в большом проекте, где много логики и этот проект будет жить десятилетия, то лучше выносить
    всю логику в отдельный сервис.

    Это будет большим плюсом, если мы через определенное время переедем на другой фреймворк и ,в целом, код выглядит
    более чисто

    У нас формируется хорошая архитекрута - расширяемая, изменяемая, легкочитаемая, переиспользуемая
    """

    @classmethod
    async def add_booking(
            cls,
            booking: SNewBooking,
            background_tasks: BackgroundTasks,
            user: Users,
    ):
        booking = await BookingDAO.add(
            user.id,
            booking.room_id,
            booking.date_from,
            booking.date_to,
        )
        if not booking:
            raise RoomCannotBeBooked
        # TypeAdapter и model_dump - это новинки версии Pydantic 2.0
        booking = TypeAdapter(SNewBooking).validate_python(booking).model_dump()
        # Celery - отдельная библиотека
        # send_booking_confirmation_email.delay(booking, user.email)
        # Background Tasks - встроено в FastAPI
        # background_tasks.add_task(send_booking_confirmation_email, booking, user.email)
        return booking
