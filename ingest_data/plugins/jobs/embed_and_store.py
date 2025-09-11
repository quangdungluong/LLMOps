import os
import sys
from pathlib import Path

# Add plugins directory to Python path
AIRFLOW_HOME = Path("/opt/airflow")
sys.path.append(str(AIRFLOW_HOME))
from plugins.utils.api import (
    find_or_create_document,
    find_or_create_knowledge_base,
    login,
)
from plugins.utils.helper import download_from_minio
from plugins.utils.vector_store import EmbeddingFactory, VectorStoreFactory


def embed_and_store():
    token = login()
    kb = find_or_create_knowledge_base(
        token, "GENERAL_KNOWLEDGE_BASE", "General knowledge base"
    )
    kb_id = kb["id"]

    embeddings = EmbeddingFactory.create()
    vector_store = VectorStoreFactory.create(
        store_type="milvus",
        collection_name=f"knowledge_base_{kb_id}",
        embedding_function=embeddings,
    )
    # List all input uri
    for input_path in os.listdir(os.getenv("INLINE_DATA_VOLUME", "/opt/data")):
        # Add document to knowledge base
        file_path = os.path.join(
            os.getenv("INLINE_DATA_VOLUME", "/opt/data"), input_path
        )
        document = find_or_create_document(token, kb_id, file_path)
        if document["status"] == "exists":
            print(f"Skipping {input_path} as it already exists in knowledge base")
            continue

        input_uri = os.path.join(
            os.getenv("MINIO_BUCKET", "llmops"), f"{os.path.basename(input_path)}.pkl"
        )
        splits = download_from_minio(input_uri)
        # Embed
        vector_store.add_documents(splits)
