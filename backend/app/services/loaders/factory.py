import os
from typing import Any

from langchain_community.document_loaders import (
    Docx2txtLoader,
    PyPDFLoader,
    TextLoader,
    UnstructuredExcelLoader,
    UnstructuredHTMLLoader,
)


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
