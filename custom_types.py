from pydantic import BaseModel
from typing import List


class RAQQueryResult(BaseModel):
    answer: str
    sources: List[str]
    num_contexts: int


class RAGSearchResult(BaseModel):
    contexts: List[str]
    sources: List[str]


class RAGUpsertResult(BaseModel):
    ingested: int


class RAGChunkAndSrc(BaseModel):
    chunks: List[str]
    source_id: str