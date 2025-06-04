import pytest
import json
from unittest.mock import patch, MagicMock, AsyncMock
import httpx
from datetime import datetime

from app.services.llm_service import LLMService
from app.models.news import NewsItem
from app.models.generation import TimeFrame, NewsStyle


@pytest.fixture
def mock_news_items():
    return [
        NewsItem(
            id="test-1",
            title="AI Breakthrough in Medicine",
            description="New AI model can predict diseases",
            content="Scientists have developed a new AI model that can predict diseases with 95% accuracy.",
            url="https://example.com/ai-medicine",
            image_url="https://example.com/image1.jpg",
            source="Tech News",
            category="technology",
            author="John Doe",
            published_at=datetime.now(),
        ),
        NewsItem(
            id="test-2",
            title="Global Climate Agreement Reached",
            description="World leaders agree on new climate goals",
            content="At the international climate summit, world leaders agreed on new ambitious goals to reduce carbon emissions.",
            url="https://example.com/climate-agreement",
            image_url="https://example.com/image2.jpg",
            source="World News",
            category="politics",
            author="Jane Smith",
            published_at=datetime.now(),
        )
    ]


@pytest.fixture
def llm_service():
    with patch("httpx.AsyncClient") as mock_client:
        service = LLMService()
        service.client = AsyncMock()
        yield service


@pytest.mark.asyncio
async def test_list_available_models(llm_service):
    # Setup mock response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "models": [
            {"name": "llama3"},
            {"name": "mistral"},
            {"name": "phi3"}
        ]
    }
    llm_service.client.get.return_value = mock_response
    
    # Call the method
    result = await llm_service.list_available_models()
    
    # Check results
    assert len(result) == 3
    assert "llama3" in result
    assert "mistral" in result
    assert "phi3" in result
    
    # Check the API call
    llm_service.client.get.assert_called_once_with("/api/tags")


@pytest.mark.asyncio
async def test_create_prompt(llm_service, mock_news_items):
    # Test prompt creation
    prompt = llm_service._create_prompt(
        news_items=mock_news_items,
        time_frame=TimeFrame.WEEK,
        style=NewsStyle.NEUTRAL,
    )
    
    # Check the prompt contains the news items
    assert "AI Breakthrough in Medicine" in prompt
    assert "Global Climate Agreement Reached" in prompt
    assert "balanced and factual" in prompt  # Neutral style


@pytest.mark.asyncio
async def test_generate_future_news(llm_service, mock_news_items):
    # Setup mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": """
[
  {
    "title": "AI Diagnostics Becomes Standard in Hospitals Worldwide",
    "content": "Following the breakthrough last week, AI diagnostic systems have been rapidly deployed in hospitals around the world. The technology, which can predict diseases with unprecedented accuracy, has already saved thousands of lives by enabling early interventions. Medical professionals report that the integration has been smoother than expected, with resistance giving way to enthusiasm as the benefits become clear.",
    "predicted_date": "2023-05-27",
    "source": "Global Health Journal",
    "category": "health"
  },
  {
    "title": "First Carbon-Negative Country Announced",
    "content": "Building on last week's climate agreement, a Nordic country has become the first to achieve carbon-negative status. Through a combination of aggressive emissions cuts, reforestation, and carbon capture technology, they are now removing more carbon from the atmosphere than they produce. Other nations are studying their approach as a potential model for accelerated climate action.",
    "predicted_date": "2023-05-27",
    "source": "Climate Watch",
    "category": "environment"
  }
]
"""
    }
    llm_service.client.post.return_value = mock_response
    
    # Call the method
    result = await llm_service.generate_future_news(
        news_items=mock_news_items,
        time_frame=TimeFrame.WEEK,
        style=NewsStyle.NEUTRAL,
    )
    
    # Check results
    assert len(result) == 2
    assert result[0].title == "AI Diagnostics Becomes Standard in Hospitals Worldwide"
    assert result[1].title == "First Carbon-Negative Country Announced"
    assert "health" in result[0].category
    assert "environment" in result[1].category
    
    # Check API call
    llm_service.client.post.assert_called_once()


import pytest
from unittest.mock import MagicMock, patch
from app.models.generation import TimeFrame, NewsStyle
from app.services.llm_service import LLMService

@pytest.mark.asyncio
async def test_generate_future_news_error_handling(llm_service, mock_news_items):
    # Setup mock response with error
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal server error"
    llm_service.client.post.return_value = mock_response
    
    # Test error handling
    with pytest.raises(Exception):
        await llm_service.generate_future_news(
            news_items=mock_news_items,
            time_frame=TimeFrame.WEEK,
            style=NewsStyle.NEUTRAL,
        )


@pytest.mark.asyncio
async def test_generate_future_news_json_error(llm_service, mock_news_items):
    # Setup mock response with invalid JSON
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": "This is not valid JSON"
    }
    llm_service.client.post.return_value = mock_response
    
    # Test fallback handling for invalid JSON
    result = await llm_service.generate_future_news(
        news_items=mock_news_items,
        time_frame=TimeFrame.WEEK,
        style=NewsStyle.NEUTRAL,
    )
    
    # Should return a fallback article
    assert len(result) == 1
    assert "Error" in result[0].category or "Generated" in result[0].title
