from datetime import date

from pydantic import BaseModel


class SchemasHotels(BaseModel):
    location: str
    date_from: date
    date_to: date
