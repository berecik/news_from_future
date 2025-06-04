from fastapi import APIRouter, HTTPException, Query, Depends, BackgroundTasks
from typing import List, Optional

from app.models.generation import (
    GenerationRequest,
    GenerationResponse,
    StreamingGenerationResponse,
)
from app.services.llm_service import LLMService, get_llm_service
from app.services.news_service import NewsService, get_news_service

router = APIRouter()


@router.post("", response_model=GenerationResponse)
async def generate_future_news(
    request: GenerationRequest,
    llm_service: LLMService = Depends(get_llm_service),
    news_service: NewsService = Depends(get_news_service),
):
    """
    Generate future news based on current news context.
    """
    try:
        # Get news for context
        news_items = await news_service.get_news(
            category=request.category,
            source=request.source,
            limit=request.context_size,
        )
        
        if not news_items:
            raise HTTPException(
                status_code=404,
                detail="No news found for the given parameters to use as context",
            )
        
        # Generate future news
        generated_news = await llm_service.generate_future_news(
            news_items=news_items,
            time_frame=request.time_frame,
            style=request.style,
            model=request.model,
        )
        
        return GenerationResponse(
            generated_news=generated_news,
            context_used=len(news_items),
            time_frame=request.time_frame,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream", response_model=StreamingGenerationResponse)
async def stream_future_news(
    request: GenerationRequest,
    llm_service: LLMService = Depends(get_llm_service),
    news_service: NewsService = Depends(get_news_service),
):
    """
    Stream future news generation based on current news context.
    """
    try:
        # Get news for context
        news_items = await news_service.get_news(
            category=request.category,
            source=request.source,
            limit=request.context_size,
        )
        
        if not news_items:
            raise HTTPException(
                status_code=404,
                detail="No news found for the given parameters to use as context",
            )
        
        # Stream generation
        return StreamingGenerationResponse(
            stream=llm_service.stream_future_news(
                news_items=news_items,
                time_frame=request.time_frame,
                style=request.style,
                model=request.model,
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models", response_model=List[str])
async def get_available_models(
    llm_service: LLMService = Depends(get_llm_service),
):
    """
    Get all available LLM models from Ollama.
    """
    try:
        return await llm_service.list_available_models()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
