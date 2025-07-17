import asyncio
import hashlib
from typing import List

from app.api.deps import get_current_user
from app.crud.document import (
    delete_document,
    get_upload_by_ids,
    upload_documents,
)
from app.crud.knowledge import (
    create_knowledge_base,
    get_document_by_id,
    get_knowledge_base_by_id,
    get_knowledge_base_by_user_id,
    preview_documents,
)
from app.crud.task import get_processing_tasks_by_ids
from app.db.session import get_db
from app.models.task import ProcessingTask
from app.models.user import User
from app.schemas.knowledge import (
    KnowledgeBaseCreate,
    KnowledgeBaseResponse,
    PreviewRequest,
)
from app.schemas.task import TaskStatus, TaskStatusResponse
from app.services.document_processor import process_document_background
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.retrieval import TestRetrievalRequest
from app.services.retrieval import retrieve_documents

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


@router.delete("/{knowledge_base_id}/documents/{document_id}")
async def delete_document_route(
    knowledge_base_id: int,
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    document = await get_document_by_id(
        db, document_id, knowledge_base_id, current_user.id
    )
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    await delete_document(db, document)
    return {"status": "success"}


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
            )
        )


@router.get("/{knowledge_base_id}/documents/tasks")
async def get_processing_tasks(
    knowledge_base_id: int,
    current_user: User = Depends(get_current_user),
    task_ids: str = Query(..., description="Comma separated list of task IDs"),
    db: AsyncSession = Depends(get_db),
):
    task_ids_list = list(map(int, task_ids.split(",")))
    knowledge_base = await get_knowledge_base_by_id(
        db, knowledge_base_id, current_user.id
    )
    if not knowledge_base:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    tasks = await get_processing_tasks_by_ids(db, task_ids_list, knowledge_base_id)
    response_data = {
        task.id: TaskStatus(
            document_id=task.document_id,
            status=task.status,
            error_message=task.error_message,
            upload_id=task.document_upload_id,
            file_name=(
                task.document_uploads.file_name if task.document_uploads else None
            ),
        )
        for task in tasks
    }
    return TaskStatusResponse.model_validate(response_data)


@router.post("/test-retrieval")
async def test_retrieval(
    test_retrieval_request: TestRetrievalRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    knowledge_base = await get_knowledge_base_by_id(
        db, test_retrieval_request.kb_id, current_user.id
    )
    if not knowledge_base:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    results = retrieve_documents(
        test_retrieval_request.query,
        knowledge_base.id,
        test_retrieval_request.top_k,
    )
    print(results)
    response = []
    for doc, score in results:
        response.append(
            {
                "document": doc.page_content,
                "metadata": doc.metadata,
                "score": float(score),
            }
        )
    return {"results": response}
