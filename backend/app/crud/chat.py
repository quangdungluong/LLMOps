from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.chat import Chat


async def get_chats_by_user_id(
    db: AsyncSession, user_id: int, skip: int = 0, limit: int = 20
):
    result = await db.execute(
        select(Chat).filter(Chat.user_id == user_id).offset(skip).limit(limit)
    )
    return result.scalars().all()
