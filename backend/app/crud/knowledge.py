from typing import Dict, List, Optional, Sequence

from app.models.document import Document, DocumentUpload
from app.models.knowledge import KnowledgeBase
from app.schemas.knowledge import DocumentBase, KnowledgeBaseCreate, PreviewResponse
from app.services.document_processor import preview_document
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload


async def create_knowledge_base(
    db: AsyncSession,
    knowledge_base: KnowledgeBaseCreate,
    user_id: int,
) -> KnowledgeBase:
    kb = KnowledgeBase(
        name=knowledge_base.name,
        description=knowledge_base.description,
        user_id=user_id,
    )
    db.add(kb)
    await db.commit()
    await db.refresh(kb)
    # load documents
    result = await db.execute(
        select(KnowledgeBase)
        .options(selectinload(KnowledgeBase.documents))
        .filter(KnowledgeBase.id == kb.id)
    )
    kb = result.scalar_one()
    return kb


async def get_knowledge_base_by_user_id(
    db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100
) -> Sequence[KnowledgeBase]:
    result = await db.execute(
        select(KnowledgeBase)
        .options(
            selectinload(KnowledgeBase.documents).selectinload(
                Document.processing_tasks
            )
        )
        .filter(KnowledgeBase.user_id == user_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def get_knowledge_base_by_id(
    db: AsyncSession, knowledge_base_id: int, user_id: int
) -> KnowledgeBase:
    result = await db.execute(
        select(KnowledgeBase)
        .options(
            selectinload(KnowledgeBase.documents).selectinload(
                Document.processing_tasks
            )
        )
        .filter(
            KnowledgeBase.id == knowledge_base_id,
            KnowledgeBase.user_id == user_id,
        )
    )
    kb = result.scalar_one_or_none()
    return kb


async def get_knowledge_base_by_ids_and_user_id(
    db: AsyncSession, knowledge_base_ids: List[int], user_id: int
) -> Sequence[KnowledgeBase]:
    result = await db.execute(
        select(KnowledgeBase)
        .options(
            selectinload(KnowledgeBase.documents).selectinload(
                Document.processing_tasks
            )
        )
        .filter(
            KnowledgeBase.id.in_(knowledge_base_ids),
            KnowledgeBase.user_id == user_id,
        )
    )
    return result.scalars().all()


async def get_knowledge_base_by_ids(
    db: AsyncSession, knowledge_base_ids: List[int]
) -> Sequence[KnowledgeBase]:
    result = await db.execute(
        select(KnowledgeBase)
        .options(
            selectinload(KnowledgeBase.documents).selectinload(
                Document.processing_tasks
            )
        )
        .filter(KnowledgeBase.id.in_(knowledge_base_ids))
    )
    return result.scalars().all()


async def get_document_by_id(
    db: AsyncSession, document_id: int, knowledge_base_id: int, user_id: int
) -> Optional[Document]:
    result = await db.execute(
        select(Document)
        .join(KnowledgeBase)
        .filter(
            Document.id == document_id,
            KnowledgeBase.id == knowledge_base_id,
            KnowledgeBase.user_id == user_id,
        )
    )
    return result.scalar_one_or_none()


async def get_upload_by_id(
    db: AsyncSession, upload_id: int, knowledge_base_id: int, user_id: int
) -> Optional[DocumentUpload]:
    result = await db.execute(
        select(DocumentUpload)
        .join(KnowledgeBase)
        .filter(
            DocumentUpload.id == upload_id,
            KnowledgeBase.id == knowledge_base_id,
            KnowledgeBase.user_id == user_id,
        )
    )
    return result.scalar_one_or_none()


async def preview_documents(
    db: AsyncSession,
    knowledge_base_id: int,
    user_id: int,
    document_ids: List[int],
    chunk_size: int,
    chunk_overlap: int,
) -> Dict[int, PreviewResponse]:
    results = {}
    for doc_id in document_ids:
        document = await get_document_by_id(db, doc_id, knowledge_base_id, user_id)
        if not document:
            upload = await get_upload_by_id(db, doc_id, knowledge_base_id, user_id)
            if not upload:
                raise ValueError(f"Document {doc_id} not found")
            file_path = upload.temp_path
        else:
            file_path = document.file_path

        preview = await preview_document(str(file_path), chunk_size, chunk_overlap)
        results[doc_id] = preview
    return results


async def create_document(
    db: AsyncSession, document: DocumentBase, knowledge_base_id: int
) -> Document:
    document = Document(
        file_name=document.file_name,
        file_path=document.file_path,
        file_size=document.file_size,
        file_hash=document.file_hash,
        content_type=document.content_type,
        knowledge_base_id=knowledge_base_id,
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)
    return document


async def get_documents_by_knowledge_base_id(
    db: AsyncSession, knowledge_base_id: int, user_id: int
) -> Sequence[Document]:
    result = await db.execute(
        select(Document)
        .join(KnowledgeBase)
        .filter(
            Document.knowledge_base_id == knowledge_base_id,
            KnowledgeBase.user_id == user_id,
        )
    )
    return result.scalars().all()
