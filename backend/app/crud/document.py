import hashlib
import os
from typing import List, Sequence

from app.core.config import settings
from app.models.document import Document, DocumentUpload
from app.models.knowledge import KnowledgeBase
from app.schemas.knowledge import KnowledgeBaseCreate
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


async def upload_documents(
    db: AsyncSession,
    knowledge_base_id: int,
    files: Sequence[UploadFile],
):
    results = []
    for file in files:
        file_content = await file.read()
        file_hash = hashlib.sha256(file_content).hexdigest()

        # check if file already exists
        result = await db.execute(
            select(Document).filter(
                Document.file_name == file.filename,
                Document.file_hash == file_hash,
                Document.knowledge_base_id == knowledge_base_id,
            )
        )
        document = result.scalar_one_or_none()
        if document:
            results.append(
                {
                    "document_id": document.id,
                    "file_name": document.file_name,
                    "status": "exists",
                }
            )
            continue

        # Save file to storage
        file_path = f"knowledge_bases/{knowledge_base_id}/{file.filename}"
        file_path = os.path.join(settings.MEDIA_ROOT, file_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(file_content)

        # Create document
        upload = DocumentUpload(
            knowledge_base_id=knowledge_base_id,
            file_name=file.filename,
            file_hash=file_hash,
            file_size=file.size,
            content_type=file.content_type,
            temp_path=file_path,
        )
        db.add(upload)
        await db.commit()
        await db.refresh(upload)

        results.append(
            {
                "upload_id": upload.id,
                "file_name": file.filename,
                "temp_path": file_path,
                "status": "pending",
                "skip_processing": False,
            }
        )

    return results


async def get_upload_by_ids(db: AsyncSession, upload_ids: List[int]):
    result = await db.execute(
        select(DocumentUpload).filter(DocumentUpload.id.in_(upload_ids))
    )
    return result.scalars().all()
