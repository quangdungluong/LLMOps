from pydantic import BaseModel


class TestRetrievalRequest(BaseModel):
    query: str
    kb_id: int
    top_k: int
