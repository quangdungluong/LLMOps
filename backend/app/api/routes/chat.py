from fastapi import APIRouter, Depends
from app.api.deps import get_current_user
from app.schemas.chat import ChatResponse
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.crud.chat import get_chats_by_user_id

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("", response_model=list[ChatResponse])
async def get_chats(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    chats = await get_chats_by_user_id(db, user.id, skip=skip, limit=limit)
    return [ChatResponse.model_validate(chat) for chat in chats]
