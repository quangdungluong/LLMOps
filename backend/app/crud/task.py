from app.models.task import ProcessingTask
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


async def get_task_by_id(db: AsyncSession, task_id: int) -> ProcessingTask:
    result = await db.execute(
        select(ProcessingTask).filter(ProcessingTask.id == task_id)
    )
    return result.scalar_one_or_none()
