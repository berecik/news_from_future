from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional

from app.models.news import NewsItem, NewsResponse
from app.services.news_service import NewsService, get_news_service

router = APIRouter()


@router.get("", response_model=NewsResponse)
async def get_news(
    category: Optional[str] = Query(None, description="Filter by news category"),
    source: Optional[str] = Query(None, description="Filter by news source"),
    limit: int = Query(10, ge=1, le=100, description="Number of news items to return"),
    skip: int = Query(0, ge=0, description="Number of news items to skip"),
    news_service: NewsService = Depends(get_news_service),
):
    """
    Retrieve current news articles.
    Optionally filter by category or source.
    """
    try:
        news_items = await news_service.get_news(
            category=category,
            source=source,
            limit=limit,
            skip=skip,
        )
        return NewsResponse(
            count=len(news_items),
            news=news_items,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories", response_model=List[str])
async def get_categories(
    news_service: NewsService = Depends(get_news_service),
):
    """
    Get all available news categories.
    """
    try:
        return await news_service.get_categories()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sources", response_model=List[str])
async def get_sources(
    news_service: NewsService = Depends(get_news_service),
):
    """
    Get all available news sources.
    """
    try:
        return await news_service.get_sources()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/refresh", response_model=NewsResponse)
async def refresh_news(
    news_service: NewsService = Depends(get_news_service),
):
    """
    Force refresh of news data from external API.
    """
    try:
        await news_service.fetch_news()
        news_items = await news_service.get_news(limit=20)
        return NewsResponse(
            count=len(news_items),
            news=news_items,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
