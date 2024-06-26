from datetime import date

from pydantic import BaseModel


class SchemasBooking(BaseModel):
    id: int
    room_id: int
    user_id: int
    date_from: date
    date_to: date
    price: int
    total_cost: int
    total_days: int

    class Config:
        from_attributes = True


class SNewBooking(BaseModel):
    room_id: int
    date_from: date
    date_to: date
