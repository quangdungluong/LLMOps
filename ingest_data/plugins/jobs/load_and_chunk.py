import os
import sys
from pathlib import Path
from typing import Any

from langchain_community.document_loaders import (
    Docx2txtLoader,
    PyPDFLoader,
    TextLoader,
    UnstructuredExcelLoader,
    UnstructuredHTMLLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Add plugins directory to Python path
AIRFLOW_HOME = Path("/opt/airflow")
sys.path.append(str(AIRFLOW_HOME))
from plugins.utils.helper import download_from_minio, upload_to_minio


class DocumentLoaderFactory:
    @staticmethod
    def create(file_path: str) -> Any:
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        if ext == ".pdf":
            return PyPDFLoader(file_path)
        elif ext == ".docx":
            return Docx2txtLoader(file_path)
        elif ext == ".xlsx":
            return UnstructuredExcelLoader(file_path)
        elif ext == ".html":
            return UnstructuredHTMLLoader(file_path)
        elif ext == ".txt":
            return TextLoader(file_path)
        elif ext == ".md":
            return TextLoader(file_path)
        else:
            return TextLoader(file_path)


def load_and_chunk():
    print("Loading and chunking documents")
    print(os.listdir(os.getenv("INLINE_DATA_VOLUME", "/opt/data")))
    for input_path in os.listdir(os.getenv("INLINE_DATA_VOLUME", "/opt/data")):
        print(f"Processing {input_path}")
        input_local_path = os.path.join(
            os.getenv("INLINE_DATA_VOLUME", "/opt/data"), input_path
        )
        output_uri = os.path.join(
            os.getenv("MINIO_BUCKET", "llmops"), f"{os.path.basename(input_path)}.pkl"
        )
        # using minio to check output_uri is exist
        if download_from_minio(output_uri):
            print(f"Skipping {input_path} as it already exists in minio")
            continue

        # Load document
        loader = DocumentLoaderFactory.create(input_local_path)
        documents = loader.load()
        # Split document into chunks
        splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=100)
        splits = splitter.split_documents(documents)
        upload_to_minio(splits, output_uri)
        print(f"Uploaded chunks to MinIO: {input_path}/{output_uri}")
