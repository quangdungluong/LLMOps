from typing import Any, Dict, Type

from langchain_core.embeddings import Embeddings

from .base import BaseVectorStore
from .milvus import MilvusVectorStore


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
