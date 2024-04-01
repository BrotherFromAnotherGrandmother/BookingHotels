from pydantic import BaseModel, EmailStr


class SchemasUserAuth(BaseModel):
    email: EmailStr
    password: str
