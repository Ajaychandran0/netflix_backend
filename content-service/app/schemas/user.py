from pydantic import BaseModel, UUID4, EmailStr

class UserContext(BaseModel):
    id: UUID4
    email: EmailStr
    role: str
