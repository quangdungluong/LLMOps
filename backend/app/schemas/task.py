from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, RootModel


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


class TaskStatus(BaseModel):
    document_id: Optional[int] = None
    status: str
    error_message: Optional[str] = None
    upload_id: Optional[int] = None
    file_name: Optional[str] = None


class TaskStatusResponse(RootModel[Dict[int, TaskStatus]]):
    pass
