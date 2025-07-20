from app.api.deps import get_current_user
from app.crud.chat import create_chat, delete_chat, get_chat_by_id, get_chats_by_user_id
from app.crud.knowledge import get_knowledge_base_by_ids_and_user_id
from app.db.session import get_db
from app.models.user import User
from app.schemas.chat import ChatCreate, ChatResponse
from app.services.chat_service import generate_response
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

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


@router.post("", response_model=ChatResponse)
async def create_chat_route(
    chat: ChatCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    knowledge_base_ids = chat.knowledge_base_ids
    knowledge_base = await get_knowledge_base_by_ids_and_user_id(
        db, knowledge_base_ids, user.id
    )
    if len(knowledge_base) != len(knowledge_base_ids):
        raise HTTPException(
            status_code=404, detail="One or more knowledge base not found"
        )
    # create chat with title, user_id, knowledge_base using create_chat
    chat = await create_chat(db, chat, user.id, knowledge_base)

    return ChatResponse.model_validate(chat)


@router.delete("/{chat_id}")
async def delete_chat_route(
    chat_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    chat = await get_chat_by_id(db, chat_id, user.id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    await delete_chat(db, chat)
    return {"status": "success"}


@router.get("/{chat_id}", response_model=ChatResponse)
async def get_chat(
    chat_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    chat = await get_chat_by_id(db, chat_id, user.id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return ChatResponse.model_validate(chat)


@router.post("/{chat_id}/messages")
async def create_message(
    chat_id: int,
    messages: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    chat = await get_chat_by_id(db, chat_id, user.id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Get the last user message
    last_user_message = messages["messages"][-1]
    if last_user_message["role"] != "user":
        raise HTTPException(status_code=400, detail="Last message must be from user")

    # Get knowledge base ids of the chat
    knowledge_base_ids = [kb.id for kb in chat.knowledge_bases]

    async def response_stream():
        async for chunk in generate_response(
            user_id=user.id,
            query=last_user_message["content"],
            messages=messages,
            knowledge_base_ids=knowledge_base_ids,
            chat_id=chat_id,
            db=db,
        ):
            yield chunk

    return StreamingResponse(response_stream(), media_type="text/event-stream")
