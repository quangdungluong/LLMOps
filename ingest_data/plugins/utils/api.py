import hashlib
import mimetypes
import os
from typing import Any, Dict

import requests

BASE_URL = os.getenv("BASE_URL", "http://llmops-backend:8000")
API_PREFIX = os.getenv("API_PREFIX", "/api/v1")
USERNAME = os.getenv("USERNAME", "admin")
PASSWORD = os.getenv("PASSWORD", "Password123")


def login(username: str = USERNAME, password: str = PASSWORD) -> str:
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/auth/token",
        data={"username": username, "password": password},
    )
    response.raise_for_status()
    return response.json()["access_token"]


def auth_headers(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def find_or_create_knowledge_base(
    token: str, name: str, description: str = ""
) -> Dict[str, Any]:
    list_kb_url = f"{BASE_URL}{API_PREFIX}/knowledge-base"
    response = requests.get(list_kb_url, headers=auth_headers(token))
    response.raise_for_status()
    kb_list = response.json()
    for kb in kb_list:
        if kb["name"] == name:
            return kb

    # Create KB if not found
    create_kb_url = f"{BASE_URL}{API_PREFIX}/knowledge-base"
    payload = {"name": name, "description": description}
    response = requests.post(create_kb_url, headers=auth_headers(token), json=payload)
    response.raise_for_status()
    return response.json()


def find_or_create_document(
    token: str, knowledge_base_id: int, file_path: str
) -> Dict[str, Any]:
    create_document_url = (
        f"{BASE_URL}{API_PREFIX}/knowledge-base/{knowledge_base_id}/documents/create"
    )
    list_document_url = (
        f"{BASE_URL}{API_PREFIX}/knowledge-base/{knowledge_base_id}/documents"
    )
    response = requests.get(list_document_url, headers=auth_headers(token))
    response.raise_for_status()
    documents = response.json()
    for doc in documents.get("documents", []):
        if doc["file_name"] == os.path.basename(file_path):
            return {"status": "exists", "document": doc}

    try:
        # get file type, file hash, file size, file name
        file_type = mimetypes.guess_type(file_path)[0]
        file_hash = hashlib.sha256(open(file_path, "rb").read()).hexdigest()
        file_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path)

        response = requests.post(
            create_document_url,
            headers=auth_headers(token),
            json={
                "file_name": file_name,
                "file_path": file_path,
                "file_size": file_size,
                "file_hash": file_hash,
                "content_type": file_type,
            },
        )
        response.raise_for_status()
        return {"status": "created", "document": response.json()}
    except Exception as e:
        print(f"Failed to create document: {e}")
