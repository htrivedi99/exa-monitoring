from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime
from enum import Enum


class CadenceEnum(str, Enum):
    HOURLY = "hourly"
    SIX_HOURS = "6hours"
    TWELVE_HOURS = "12hours"
    DAILY = "daily"
    WEEKLY = "weekly"


class MonitorStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"


class MonitorCreate(BaseModel):
    query: str
    cadence: CadenceEnum
    webhook_url: Optional[str] = None


class MonitorUpdate(BaseModel):
    query: Optional[str] = None
    cadence: Optional[CadenceEnum] = None
    webhook_url: Optional[str] = None
    status: Optional[MonitorStatus] = None


class Monitor(BaseModel):
    id: str
    query: str
    cadence: CadenceEnum
    webhook_url: Optional[str] = None
    created_at: datetime
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    seen_urls: List[str] = []
    status: MonitorStatus = MonitorStatus.ACTIVE

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class MonitorResponse(BaseModel):
    """Public API response (without seen_urls list for performance)"""
    id: str
    query: str
    cadence: CadenceEnum
    webhook_url: Optional[str] = None
    created_at: datetime
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    seen_urls_count: int
    status: MonitorStatus

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
