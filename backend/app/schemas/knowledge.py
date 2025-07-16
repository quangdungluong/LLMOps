from datetime import datetime
from typing import List, Optional

from app.schemas.task import ProcessingTask
from pydantic import BaseModel, Field


class KnowledgeBaseBase(BaseModel):
    name: str
    description: Optional[str] = None


class KnowledgeBaseCreate(KnowledgeBaseBase):
    pass


class DocumentBase(BaseModel):
    file_name: str
    file_path: str
    file_size: int
    file_hash: str
    content_type: str


class DocumentResponse(DocumentBase):
    id: int
    knowledge_base_id: int
    created_at: datetime
    updated_at: datetime
    processing_tasks: List[ProcessingTask] = []

    class Config:
        from_attributes = True


class KnowledgeBaseResponse(KnowledgeBaseBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    documents: List[DocumentResponse] = []

    class Config:
        from_attributes = True


class PreviewRequest(BaseModel):
    document_ids: List[int]
    chunk_size: int = 1000
    chunk_overlap: int = 200


class TextChunk(BaseModel):
    content: str
    metadata: Optional[dict] = None


class PreviewResponse(BaseModel):
    chunks: List[TextChunk]
    total_chunks: int
