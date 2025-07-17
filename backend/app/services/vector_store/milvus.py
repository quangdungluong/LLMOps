from typing import Any, List, Tuple

from app.core.config import settings
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.retrievers import BaseRetriever
from langchain_milvus import Milvus

from .base import BaseVectorStore


class MilvusVectorStore(BaseVectorStore):
    def __init__(self, collection_name: str, embedding_function: Embeddings, **kwargs):
        self._store = Milvus(
            embedding_function=embedding_function,
            connection_args={
                "uri": settings.MILVUS_URI,
            },
            collection_name=collection_name,
            enable_dynamic_field=True,
        )

    def add_documents(self, documents: List[Document]) -> None:
        self._store.add_documents(documents)

    def delete(self, ids: List[str]) -> None:
        self._store.delete(ids)

    def as_retriever(self, **kwargs: Any) -> BaseRetriever:
        return self._store.as_retriever(**kwargs)

    def similarity_search(
        self, query: str, k: int = 4, **kwargs: Any
    ) -> List[Document]:
        return self._store.similarity_search(query, k, **kwargs)

    def similarity_search_with_score(
        self, query: str, k: int = 4, **kwargs: Any
    ) -> List[Tuple[Document, float]]:
        return self._store.similarity_search_with_score(query, k, **kwargs)

    def delete_collection(self) -> None:
        self._store._milvus_client.delete(self._store.collection_name)
