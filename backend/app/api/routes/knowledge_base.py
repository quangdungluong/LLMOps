import asyncio
import hashlib
from typing import List

from app.api.deps import get_current_user
from app.crud.document import get_upload_by_ids, upload_documents
from app.crud.knowledge import (
    create_knowledge_base,
    get_knowledge_base_by_id,
    get_knowledge_base_by_user_id,
    preview_documents,
)
from app.db.session import get_db
from app.models.task import ProcessingTask
from app.models.user import User
from app.schemas.knowledge import (
    KnowledgeBaseCreate,
    KnowledgeBaseResponse,
    PreviewRequest,
)
from app.services.document_processor import process_document_background
from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/knowledge-base", tags=["knowledge-base"])


@router.post("", response_model=KnowledgeBaseResponse)
async def create_knowledge_base_route(
    knowledge_base: KnowledgeBaseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> KnowledgeBaseResponse:
    kb = await create_knowledge_base(db, knowledge_base, current_user.id)
    return KnowledgeBaseResponse.model_validate(kb)


@router.get("", response_model=List[KnowledgeBaseResponse])
async def get_knowledge_bases(
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> List[KnowledgeBaseResponse]:
    knowledge_bases = await get_knowledge_base_by_user_id(
        db, current_user.id, skip=skip, limit=limit
    )
    return [KnowledgeBaseResponse.model_validate(kb) for kb in knowledge_bases]


@router.get("/{knowledge_base_id}", response_model=KnowledgeBaseResponse)
async def get_knowledge_base(
    knowledge_base_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> KnowledgeBaseResponse:
    kb = await get_knowledge_base_by_id(db, knowledge_base_id, current_user.id)
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    return KnowledgeBaseResponse.model_validate(kb)


@router.put("/{knowledge_base_id}", response_model=KnowledgeBaseResponse)
async def update_knowledge_base(
    knowledge_base_id: int,
    knowledge_base: KnowledgeBaseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> KnowledgeBaseResponse:
    pass


@router.delete("/{knowledge_base_id}", response_model=KnowledgeBaseResponse)
async def delete_knowledge_base(
    knowledge_base_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> KnowledgeBaseResponse:
    pass


@router.post("/{knowledge_base_id}/documents/upload")
async def upload_documents_route(
    knowledge_base_id: int,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    kb = await get_knowledge_base_by_id(db, knowledge_base_id, current_user.id)
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    results = await upload_documents(db, knowledge_base_id, files)
    return results


@router.post("/{knowledge_base_id}/documents/process")
async def process_documents_route(
    knowledge_base_id: int,
    background_tasks: BackgroundTasks,
    upload_results: List[dict],
    # preview_request: PreviewRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    kb = await get_knowledge_base_by_id(db, knowledge_base_id, current_user.id)
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    task_info = []
    upload_ids = []
    for result in upload_results:
        if result.get("skip_processing"):
            continue
        upload_ids.append(result["upload_id"])

    if not upload_ids:
        return {"tasks": []}
    uploads = await get_upload_by_ids(db, upload_ids)
    uploads_dict = {upload.id: upload for upload in uploads}

    all_tasks = []
    for upload_id in upload_ids:
        upload = uploads_dict[upload_id]
        if not upload:
            continue
        task = ProcessingTask(
            knowledge_base_id=knowledge_base_id,
            document_upload_id=upload.id,
            status="pending",
        )
        all_tasks.append(task)

    db.add_all(all_tasks)
    await db.commit()

    for task in all_tasks:
        await db.refresh(task)

    task_data = []
    for i, upload_id in enumerate(upload_ids):
        if i < len(all_tasks):
            task = all_tasks[i]
            upload = uploads_dict.get(upload_id)

            task_info.append({"upload_id": upload_id, "task_id": task.id})

            if upload:
                task_data.append(
                    {
                        "task_id": task.id,
                        "upload_id": upload_id,
                        "temp_path": upload.temp_path,
                        "file_name": upload.file_name,
                    }
                )

    background_tasks.add_task(
        add_processing_tasks_to_queue,
        task_data,
        knowledge_base_id,
        1000,
        200,
        db,
    )

    return {"tasks": task_info}


@router.post("/{knowledge_base_id}/documents/preview")
async def preview_documents_route(
    knowledge_base_id: int,
    preview_request: PreviewRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    results = await preview_documents(
        db,
        knowledge_base_id,
        current_user.id,
        preview_request.document_ids,
        preview_request.chunk_size,
        preview_request.chunk_overlap,
    )
    return results


async def add_processing_tasks_to_queue(
    task_data: List[dict],
    knowledge_base_id: int,
    chunk_size: int,
    chunk_overlap: int,
    db: AsyncSession,
):
    for data in task_data:
        asyncio.create_task(
            process_document_background(
                data["temp_path"],
                data["file_name"],
                knowledge_base_id,
                data["task_id"],
                chunk_size,
                chunk_overlap,
                db,
            )
        )
