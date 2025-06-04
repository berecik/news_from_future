import pytest
from unittest.mock import patch, MagicMock
from app.services.news_service import NewsService
from app.models.news import NewsItem
from datetime import datetime

@pytest.fixture
def mock_news_service():
    # Create a mock news service with test setup
    with patch("app.services.news_service.settings") as mock_settings:
        # Configure mock settings
        mock_settings.NEWSDATA_API_KEY = "test_api_key"
        mock_settings.NEWS_CATEGORIES = "business,technology,science"
        mock_settings.NEWS_SOURCES = ""
        mock_settings.NEWS_STORAGE_FILE = "test_cache.json"
        
        news_service = NewsService()
        return news_service

@pytest.fixture
def mock_news_items():
    return [
        NewsItem(
            id="test-1",
            title="Test News 1",
            description="Test description 1",
            content="Test content 1",
            url="https://example.com/1",
            image_url="https://example.com/image1.jpg",
            source="Test Source",
            category="politics",
            author="Test Author",
            published_at=datetime.now(),
        ),
        NewsItem(
            id="test-2",
            title="Test News 2",
            description="Test description 2",
            content="Test content 2",
            url="https://example.com/2",
            image_url="https://example.com/image2.jpg",
            source="Test Source 2",
            category="technology",
            author="Test Author 2",
            published_at=datetime.now(),
        ),
    ]

@pytest.fixture
def llm_service():
    with patch("app.services.llm_service.settings") as mock_settings:
        from app.services.llm_service import LLMService
        
        # Configure mock settings
        mock_settings.OLLAMA_BASE_URL = "http://localhost:11434"
        mock_settings.OLLAMA_MODEL = "llama3"
        
        # Create LLM service with mocked client
        service = LLMService()
        service.client = MagicMock()
        
        return service
