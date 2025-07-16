from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ProcessingTaskBase(BaseModel):
    status: str
    error_message: Optional[str] = None


class ProcessingTask(ProcessingTaskBase):
    id: int
    document_id: int
    knowledge_base_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
