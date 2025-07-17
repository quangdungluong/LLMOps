from typing import List

from app.models.task import ProcessingTask
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload


async def get_task_by_id(db: AsyncSession, task_id: int) -> ProcessingTask:
    result = await db.execute(
        select(ProcessingTask)
        .options(selectinload(ProcessingTask.document_uploads))
        .filter(ProcessingTask.id == task_id)
    )
    return result.scalar_one_or_none()


async def get_processing_tasks_by_ids(
    db: AsyncSession,
    task_ids: List[int],
    knowledge_base_id: int,
) -> List[ProcessingTask]:
    result = await db.execute(
        select(ProcessingTask)
        .options(selectinload(ProcessingTask.document_uploads))
        .filter(
            ProcessingTask.id.in_(task_ids),
            ProcessingTask.knowledge_base_id == knowledge_base_id,
        )
    )
    return result.scalars().all()
