from app.core.config import settings
from app.services.embeddings.embedding_factory import EmbeddingFactory
from app.services.vector_store.factory import VectorStoreFactory


def retrieve_documents(query: str, knowledge_base_id: int, top_k: int = 10):
    embeddings = EmbeddingFactory.create()
    vector_store = VectorStoreFactory.create(
        store_type=settings.VECTOR_STORE_PROVIDER,
        collection_name=f"knowledge_base_{knowledge_base_id}",
        embedding_function=embeddings,
    )
    results = vector_store.similarity_search_with_score(query, k=top_k)
    return results
