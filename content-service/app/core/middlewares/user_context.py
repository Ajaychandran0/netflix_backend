from fastapi import Header, HTTPException
from app.schemas.user import UserContext
from uuid import UUID
from typing import Annotated

async def get_user_context(
    x_user_id: Annotated[str, Header()],
    x_user_email: Annotated[str, Header()],
    x_user_role: Annotated[str, Header()],
) -> UserContext:
    try:
        print(f"User ID: {x_user_id}, Email: {x_user_email}, Role: {x_user_role}")
        return UserContext(
            id=UUID(x_user_id),
            email=x_user_email,
            role=x_user_role
        )
    except Exception as e:
        print(f"Error parsing user headers: {e}")
        raise HTTPException(status_code=400, detail="Invalid or missing user headers")
