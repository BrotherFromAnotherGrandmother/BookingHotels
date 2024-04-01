from datetime import date, datetime

from fastapi import Query

from app.hotels.rooms.dao import RoomDAO
from app.hotels.router import router


@router.get("/{hotel_id}/rooms")
async def get_rooms(
        hotel_id: int,
        date_from: date = Query(..., description=f"Например, {datetime.now().date()}"),
        date_to: date = Query(..., description=f"Например, {datetime.now().date()}"),
):
    """Возвращает список всех номеров определенного отеля"""
    rooms = await RoomDAO.search_for_rooms(hotel_id, date_from, date_to)
    return rooms
