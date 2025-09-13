from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple, Type

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.retrievers import BaseRetriever
from langchain_milvus import Milvus
from langchain_ollama import OllamaEmbeddings


class BaseVectorStore(ABC):
    """Abstract base class for vector store implementations"""

    @abstractmethod
    def __init__(self, collection_name: str, embedding_function: Embeddings, **kwargs):
        """Initialize the vector store"""
        pass

    @abstractmethod
    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to the vector store"""
        pass

    @abstractmethod
    def delete(self, ids: List[str]) -> None:
        """Delete documents from the vector store"""
        pass

    @abstractmethod
    def as_retriever(self, **kwargs: Any):
        """Return a retriever interface for the vector store"""
        pass

    @abstractmethod
    def similarity_search(
        self, query: str, k: int = 4, **kwargs: Any
    ) -> List[Document]:
        """Search for similar documents"""
        pass

    @abstractmethod
    def similarity_search_with_score(
        self, query: str, k: int = 4, **kwargs: Any
    ) -> List[Document]:
        """Search for similar documents with score"""
        pass

    @abstractmethod
    def delete_collection(self) -> None:
        """Delete the entire collection"""
        pass


class MilvusVectorStore(BaseVectorStore):
    def __init__(self, collection_name: str, embedding_function: Embeddings, **kwargs):
        self.collection_name = collection_name
        self._store = Milvus(
            embedding_function=embedding_function,
            connection_args={
                "uri": "http://milvus-standalone:19530",
            },
            collection_name=collection_name,
            enable_dynamic_field=True,
        )

    def add_documents(self, documents: List[Document]) -> None:
        self._store.add_documents(documents)

    def delete(self, ids: List[str]) -> None:
        self._store.delete(ids)

    def delete_by_document_id(self, document_id: int) -> None:
        try:
            results = self._store._milvus_client.query(
                collection_name=self.collection_name,
                filter=f"document_id == {document_id}",
                output_fields=["pk"],
            )
            if results:
                ids_to_delete = [res["pk"] for res in results]
                self.delete(ids_to_delete)
        except Exception as e:
            print(f"Failed to delete document from Milvus: {e}")

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


class EmbeddingFactory:
    @staticmethod
    def create():
        embedding_provider = "ollama"

        if embedding_provider == "ollama":
            return OllamaEmbeddings(
                model="nomic-embed-text",
                base_url="http://host.docker.internal:11434",
            )
        else:
            raise ValueError(f"Unsupported embedding provider: {embedding_provider}")


class VectorStoreFactory:
    _stores: Dict[str, Type[BaseVectorStore]] = {"milvus": MilvusVectorStore}

    @classmethod
    def create(
        cls,
        store_type: str,
        collection_name: str,
        embedding_function: Embeddings,
        **kwargs: Any,
    ) -> BaseVectorStore:
        store_class = cls._stores.get(store_type.lower())
        if not store_class:
            raise ValueError(f"Unsupported vector store provider: {store_type}")

        return store_class(collection_name, embedding_function, **kwargs)
