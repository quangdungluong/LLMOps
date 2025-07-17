import hashlib
import os
import re
import traceback

from app.core.config import settings
from app.crud.task import get_task_by_id
from app.db.session import AsyncSessionLocal
from app.models.document import Document
from app.schemas.knowledge import PreviewResponse, TextChunk
from app.services.embeddings.embedding_factory import EmbeddingFactory
from app.services.vector_store.factory import VectorStoreFactory
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document as LangchainDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.ext.asyncio import AsyncSession

MILVUS_FIELD_NAME_PATTERN = re.compile(r"[^a-zA-Z0-9_]")


def sanitize_metadata_field_name(name: str) -> str:
    return MILVUS_FIELD_NAME_PATTERN.sub("_", name)


def sanitize_metadata(doc: LangchainDocument):
    sanitized = {sanitize_metadata_field_name(k): v for k, v in doc.metadata.items()}
    doc.metadata = sanitized
    return doc


async def preview_document(
    file_path: str, chunk_size: int, chunk_overlap: int
) -> PreviewResponse:
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    if ext == ".pdf":
        loader = PyPDFLoader(file_path)

    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    chunks = text_splitter.split_documents(documents)

    # Convert to preview response
    preview_chunks = [
        TextChunk(content=chunk.page_content, metadata=chunk.metadata)
        for chunk in chunks
    ]
    return PreviewResponse(chunks=preview_chunks, total_chunks=len(chunks))


async def process_document_background(
    temp_path: str,
    file_name: str,
    knowledge_base_id: int,
    task_id: int,
    chunk_size: int,
    chunk_overlap: int,
):
    async with AsyncSessionLocal() as db:
        task = await get_task_by_id(db, task_id)

        if not task:
            print(f"Task {task_id} not found")
            return

        try:
            task.status = "processing"
            await db.commit()

            _, ext = os.path.splitext(file_name)
            ext = ext.lower()

            if ext == ".pdf":
                loader = PyPDFLoader(temp_path)

            documents = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )
            chunks = text_splitter.split_documents(documents)

            embeddings = EmbeddingFactory.create()
            vector_store = VectorStoreFactory.create(
                store_type=settings.VECTOR_STORE_PROVIDER,
                collection_name=f"knowledge_base_{knowledge_base_id}",
                embedding_function=embeddings,
            )

            print(f"Task: {task_id}: Creating document records")
            document = Document(
                file_name=file_name,
                file_path=temp_path,
                file_size=task.document_uploads.file_size,
                file_hash=task.document_uploads.file_hash,
                content_type=task.document_uploads.content_type,
                knowledge_base_id=knowledge_base_id,
            )
            db.add(document)
            await db.commit()
            await db.refresh(document)

            # Store document chunks
            for i, chunk in enumerate(chunks):
                chunk_id = hashlib.sha256(
                    f"{knowledge_base_id}:{file_name}:{chunk.page_content}".encode()
                ).hexdigest()

                chunk.metadata["source"] = file_name
                chunk.metadata["knowledge_base_id"] = knowledge_base_id
                chunk.metadata["document_id"] = document.id
                chunk.metadata["chunk_id"] = chunk_id

            # Add chunk to vectorstore
            chunks = [sanitize_metadata(chunk) for chunk in chunks]
            vector_store.add_documents(chunks)
            task.status = "completed"
            task.document_id = document.id

            upload = task.document_uploads
            if upload:
                upload.status = "completed"

            await db.commit()
            print(f"Task: {task_id}: Document processed")
        except Exception as e:
            traceback.print_exc()
            print(f"Error previewing document {file_name}: {e}")
            task.status = "error"
            task.error_message = str(e)
            await db.commit()
            return
