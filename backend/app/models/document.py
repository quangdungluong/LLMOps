from datetime import datetime, timezone

from app.models.base import Base, TimestampMixin
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship


class Document(Base, TimestampMixin):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String(255), nullable=False)
    file_hash = Column(String(255), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    content_type = Column(String(255), nullable=False)
    knowledge_base_id = Column(
        Integer, ForeignKey("knowledge_bases.id"), nullable=False
    )

    # Relationships
    knowledge_base = relationship("KnowledgeBase", back_populates="documents")

    __table_args__ = (
        UniqueConstraint(
            "knowledge_base_id",
            "file_name",
            name="uq_knowledge_base_id_file_name",
        ),
    )


class DocumentUpload(Base):
    __tablename__ = "document_uploads"

    id = Column(Integer, primary_key=True, index=True)
    knowledge_base_id = Column(
        Integer, ForeignKey("knowledge_bases.id", ondelete="CASCADE"), nullable=False
    )
    file_name = Column(String(255), nullable=False)
    file_hash = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    content_type = Column(String(255), nullable=False)
    temp_path = Column(String(255), nullable=False)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc)
    )
    status = Column(String(255), nullable=False, server_default="pending")
    error_message = Column(Text, nullable=True)

    # Relationships
    knowledge_base = relationship("KnowledgeBase", back_populates="document_uploads")
