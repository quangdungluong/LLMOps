from datetime import datetime, timezone

from app.models.base import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship


class ProcessingTask(Base):
    __tablename__ = "processing_tasks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id"), nullable=True)
    document_upload_id = Column(
        Integer, ForeignKey("document_uploads.id"), nullable=True
    )
    status = Column(String(50), default="pending")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    # Relationships
    document = relationship("Document", back_populates="processing_tasks")
    knowledge_base = relationship("KnowledgeBase", back_populates="processing_tasks")
    document_uploads = relationship("DocumentUpload", back_populates="processing_tasks")
