from sqlalchemy import Column, Integer, String, ForeignKey, Table

from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin

chat_knowledge_bases = Table(
    "chat_knowledge_bases",
    Base.metadata,
    Column("chat_id", Integer, ForeignKey("chats.id"), primary_key=True),
    Column(
        "knowledge_base_id", Integer, ForeignKey("knowledge_bases.id"), primary_key=True
    ),
)


class Chat(Base, TimestampMixin):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    messages = relationship(
        "Message", back_populates="chat", cascade="all, delete-orphan"
    )
    user = relationship("User", back_populates="chats")
    knowledge_bases = relationship(
        "KnowledgeBase", secondary=chat_knowledge_bases, backref="chats"
    )


class Message(Base, TimestampMixin):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    content = Column(String, nullable=False)
    role = Column(String, nullable=False)

    chat = relationship("Chat", back_populates="messages")
