from pydantic import BaseModel, Field
from typing import List, Optional, Generator, Any
from enum import Enum
from datetime import datetime


class TimeFrame(str, Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class NewsStyle(str, Enum):
    NEUTRAL = "neutral"
    OPTIMISTIC = "optimistic"
    PESSIMISTIC = "pessimistic"
    SENSATIONAL = "sensational"
    ANALYTICAL = "analytical"


class GenerationRequest(BaseModel):
    category: Optional[str] = None
    source: Optional[str] = None
    time_frame: TimeFrame = TimeFrame.WEEK
    style: NewsStyle = NewsStyle.NEUTRAL
    context_size: int = Field(10, ge=1, le=50)
    model: Optional[str] = None


class GeneratedNewsItem(BaseModel):
    title: str
    content: str
    predicted_date: datetime
    source: str
    category: Optional[str] = None


class GenerationResponse(BaseModel):
    generated_news: List[GeneratedNewsItem]
    context_used: int
    time_frame: TimeFrame
    created_at: datetime = Field(default_factory=datetime.now)


class StreamingGenerationResponse(BaseModel):
    stream: Generator[str, Any, None]
