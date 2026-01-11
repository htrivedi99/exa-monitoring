from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime
from enum import Enum


class URLContent(BaseModel):
    url: str
    title: str
    published_date: Optional[str] = None
    summary: str
    author: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class LLMAnalysis(BaseModel):
    is_significant: bool
    summary: str
    key_changes: List[str]
    reasoning: str


class ResultStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class MonitorResult(BaseModel):
    id: str
    monitor_id: str
    run_at: datetime
    new_urls_count: int
    urls: List[URLContent]
    llm_analysis: Optional[LLMAnalysis] = None
    webhook_sent: bool = False
    webhook_error: Optional[str] = None
    status: ResultStatus
    error_message: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
