from datetime import datetime
from typing import List
from pydantic import BaseModel


class MessageBase(BaseModel):
    content: str
    role: str


class MessageCreate(MessageBase):
    chat_id: int


class MessageResponse(MessageBase):
    id: int
    chat_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatBase(BaseModel):
    title: str


class ChatResponse(ChatBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []
    knowledge_base_ids: List[int] = []

    class Config:
        from_attributes = True
