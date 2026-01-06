from typing import List
from pydantic import BaseModel

class FileResponse(BaseModel):
    alias: str
    url: str

class BatchRequest(BaseModel):
    aliases: List[str]

class BatchResponse(BaseModel):
    results: List[FileResponse]
    not_found: List[str]

class TagSearchResponse(BaseModel):
    results: List[FileResponse]
    total_count: int

class ErrorResponse(BaseModel):
    error: str
    detail: str

class HealthResponse(BaseModel):
    status: str
