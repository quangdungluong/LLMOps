from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.chat import Chat
from app.schemas.chat import ChatCreate
from app.models.knowledge import KnowledgeBase
from typing import List


async def get_chats_by_user_id(
    db: AsyncSession, user_id: int, skip: int = 0, limit: int = 20
):
    result = await db.execute(
        select(Chat)
        .filter(Chat.user_id == user_id)
        .options(selectinload(Chat.messages), selectinload(Chat.knowledge_bases))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def get_chat_by_id(db: AsyncSession, chat_id: int, user_id: int):
    result = await db.execute(
        select(Chat)
        .filter(Chat.id == chat_id, Chat.user_id == user_id)
        .options(selectinload(Chat.messages), selectinload(Chat.knowledge_bases))
    )
    return result.scalar_one_or_none()


async def create_chat(
    db: AsyncSession,
    chat: ChatCreate,
    user_id: int,
    knowledge_base: List[KnowledgeBase],
) -> Chat:
    db_chat = Chat(
        title=chat.title,
        user_id=user_id,
    )
    db_chat.knowledge_bases.extend(knowledge_base)

    db.add(db_chat)
    await db.commit()
    await db.refresh(db_chat)

    # To get the chat with the relationships loaded, we query it back from the db
    query = (
        select(Chat)
        .where(Chat.id == db_chat.id)
        .options(selectinload(Chat.messages), selectinload(Chat.knowledge_bases))
    )
    result = await db.execute(query)
    return result.scalar_one()


async def delete_chat(db: AsyncSession, chat: Chat):
    # Delete chat and its messages
    await db.delete(chat)
    await db.commit()
