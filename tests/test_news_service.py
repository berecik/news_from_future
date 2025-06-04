import pytest
import json
from unittest.mock import patch, MagicMock, mock_open
import os
from datetime import datetime
import httpx

from app.services.news_service import NewsService
from app.models.news import NewsItem


@pytest.fixture
def mock_newsapi_response():
    return {
        "status": "ok",
        "totalResults": 2,
        "articles": [
            {
                "source": {"id": "test-source", "name": "Test Source"},
                "author": "Test Author",
                "title": "Test News Title",
                "description": "Test news description",
                "url": "https://example.com/news/1",
                "urlToImage": "https://example.com/image1.jpg",
                "publishedAt": "2023-05-20T12:00:00Z",
                "content": "Test news content"
            },
            {
                "source": {"id": "test-source-2", "name": "Test Source 2"},
                "author": "Test Author 2",
                "title": "Test News Title 2",
                "description": "Test news description 2",
                "url": "https://example.com/news/2",
                "urlToImage": "https://example.com/image2.jpg",
                "publishedAt": "2023-05-20T13:00:00Z",
                "content": "Test news content 2"
            }
        ]
    }


@pytest.fixture
def mock_news_service():
    with patch("newsapi.NewsApiClient") as mock_newsapi:
        service = NewsService()
        service.newsapi = mock_newsapi
        yield service


@pytest.mark.asyncio
async def test_fetch_news(mock_news_service, mock_newsdata_response):
    # Setup mock httpx client
    with patch("httpx.AsyncClient.get") as mock_get:
        # Create a mock response
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = mock_newsdata_response
        mock_get.return_value = mock_response

        # Mock file operations
        with patch("builtins.open", mock_open()) as mock_file, \
             patch("json.dump") as mock_json_dump, \
             patch("os.path.exists", return_value=False):

            # Call the method
            result = await mock_news_service.fetch_news()

            # Check httpx client was called
            assert mock_get.call_count > 0
            
            # Check we got results
            assert len(result) > 0
            assert isinstance(result[0], NewsItem)
        
        # Check the results
        assert len(result) == 2
        assert result[0].title == "Test News Title"
        assert result[1].title == "Test News Title 2"
        
        # Check that cache was saved
        mock_file.assert_called()
        mock_json_dump.assert_called()


@pytest.mark.asyncio
async def test_get_news_with_filters(mock_news_service):
    # Setup test data
    mock_news_service.news_cache = [
        NewsItem(
            id="test-1",
            title="Politics News",
            description="Politics description",
            content="Politics content",
            url="https://example.com/politics",
            image_url="https://example.com/image1.jpg",
            source="CNN",
            category="politics",
            author="Author 1",
            published_at=datetime.now(),
        ),
        NewsItem(
            id="test-2",
            title="Technology News",
            description="Tech description",
            content="Tech content",
            url="https://example.com/tech",
            image_url="https://example.com/image2.jpg",
            source="BBC",
            category="technology",
            author="Author 2",
            published_at=datetime.now(),
        )
    ]
    
    # Test category filter
    result = await mock_news_service.get_news(category="politics")
    assert len(result) == 1
    assert result[0].title == "Politics News"
    
    # Test source filter
    result = await mock_news_service.get_news(source="BBC")
    assert len(result) == 1
    assert result[0].title == "Technology News"
    
    # Test pagination
    result = await mock_news_service.get_news(limit=1)
    assert len(result) == 1


@pytest.mark.asyncio
async def test_get_categories(mock_news_service):
    # Setup
    mock_news_service.categories = ["politics", "technology", "business"]
    
    # Test
    result = await mock_news_service.get_categories()
    
    # Check results
    assert len(result) == 3
    assert "politics" in result
    assert "technology" in result
    assert "business" in result


@pytest.mark.asyncio
async def test_get_sources(mock_news_service):
    # Setup test data
    mock_news_service.news_cache = [
        NewsItem(
            id="test-1",
            title="CNN News",
            description="CNN description",
            content="CNN content",
            url="https://cnn.com",
            image_url="https://cnn.com/image.jpg",
            source="CNN",
            category="politics",
            author="CNN Author",
            published_at=datetime.now(),
        ),
        NewsItem(
            id="test-2",
            title="BBC News",
            description="BBC description",
            content="BBC content",
            url="https://bbc.com",
            image_url="https://bbc.com/image.jpg",
            source="BBC",
            category="general",
            author="BBC Author",
            published_at=datetime.now(),
        )
    ]
    
    # Test
    result = await mock_news_service.get_sources()
    
    # Check results
    assert len(result) == 2
    assert "CNN" in result
    assert "BBC" in result


def test_parse_news_items(mock_news_service, mock_newsapi_response):
    # Test parsing news items from API response
    result = mock_news_service._parse_news_items(mock_newsapi_response)
    
    # Check results
    assert len(result) == 2
    assert result[0].title == "Test News Title"
    assert result[0].source == "Test Source"
    assert result[1].title == "Test News Title 2"
    assert result[1].source == "Test Source 2"
