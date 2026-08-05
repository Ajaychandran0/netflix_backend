from pydantic import BaseModel, EmailStr
from uuid import UUID

class UserContext(BaseModel):
    id: UUID
    email: EmailStr
    role: str
