import asyncio
from datetime import date, datetime

from fastapi import APIRouter, Query
from fastapi_cache.decorator import cache

from app.hotels.dao import HotelDAO
from app.hotels.schemas import SchemasHotels

router = APIRouter(
    prefix="/hotels",
    tags=["Отели"]
)


@router.get("")
@cache(expire=60)
async def get_hotels_by_location_and_time(
        location: str,
        data_from: date = Query(..., description=f"Например, {datetime.now().date()}"),
        data_to: date = Query(..., description=f"Например, {datetime.now().date()}"),
):
    hotels = await HotelDAO.search_hotels_by_location_and_time(location, data_from, data_to)
    return hotels


@router.get("/id/{hotel_id}")
async def get_specific_hotel(
        hotel_id: int
):
    response_one_hotel = await HotelDAO.get_specific_hotel(hotel_id)
    return response_one_hotel
