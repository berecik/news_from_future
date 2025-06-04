from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class NewsItem(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    url: str
    image_url: Optional[str] = None
    source: str
    category: Optional[str] = None
    author: Optional[str] = None
    published_at: datetime
    
    class Config:
        frozen = True


class NewsResponse(BaseModel):
    count: int
    news: List[NewsItem]
