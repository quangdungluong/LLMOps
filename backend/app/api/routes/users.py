from typing import Any

from app.crud.user import create_user, get_user_by_email, get_user_by_username
from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse
from fastapi import APIRouter, Depends, HTTPException
from requests.exceptions import RequestException
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserResponse)
async def register_user(
    *, db: AsyncSession = Depends(get_db), user_in: UserCreate
) -> Any:
    """
    Register a new user.
    """
    try:
        # Check if user with this email exists
        user = await get_user_by_email(db, user_in.email)
        if user:
            raise HTTPException(
                status_code=400,
                detail="User with this email already exists",
            )
        # Check if user with this username exists
        user = await get_user_by_username(db, user_in.username)
        if user:
            raise HTTPException(
                status_code=400,
                detail="User with this username already exists",
            )
        # Create new user
        user = await create_user(db, user_in)
        return user
    except RequestException as e:
        raise HTTPException(
            status_code=503,
            detail="Network error or server is unreachable. Please try again later.",
        ) from e
