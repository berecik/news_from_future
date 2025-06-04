import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json

from main import app
from app.models.news import NewsItem
from datetime import datetime


@pytest.fixture
def client():
    return TestClient(app)


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


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "online"


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@patch("app.services.news_service.NewsService.get_news")
def test_get_news_endpoint(mock_get_news, client, mock_news_items):
    mock_get_news.return_value = mock_news_items
    
    response = client.get("/api/news")
    assert response.status_code == 200
    
    data = response.json()
    assert "count" in data
    assert data["count"] == 2
    assert len(data["news"]) == 2
    assert data["news"][0]["title"] == "Test News 1"
    assert data["news"][1]["title"] == "Test News 2"


@patch("app.services.news_service.NewsService.get_news")
def test_get_news_with_filters(mock_get_news, client, mock_news_items):
    # Filter to only return the technology news item
    mock_get_news.return_value = [mock_news_items[1]]
    
    response = client.get("/api/news?category=technology")
    assert response.status_code == 200
    
    data = response.json()
    assert data["count"] == 1
    assert data["news"][0]["title"] == "Test News 2"
    assert data["news"][0]["category"] == "technology"


@patch("app.services.news_service.NewsService.get_categories")
def test_get_categories(mock_get_categories, client):
    mock_get_categories.return_value = ["politics", "technology", "business"]
    
    response = client.get("/api/news/categories")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 3
    assert "politics" in data
    assert "technology" in data
    assert "business" in data


@patch("app.services.news_service.NewsService.get_sources")
def test_get_sources(mock_get_sources, client):
    mock_get_sources.return_value = ["Test Source", "Test Source 2"]
    
    response = client.get("/api/news/sources")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    assert "Test Source" in data
    assert "Test Source 2" in data


@patch("app.services.llm_service.LLMService.generate_future_news")
@patch("app.services.news_service.NewsService.get_news")
def test_generate_future_news(mock_get_news, mock_generate, client, mock_news_items):
    mock_get_news.return_value = mock_news_items
    
    # Mock the LLM response
    mock_generate.return_value = [
        {
            "title": "Future News Title",
            "content": "Future news content",
            "predicted_date": datetime.now(),
            "source": "AI News Generator",
            "category": "politics",
        }
    ]
    
    request_data = {
        "category": "politics",
        "time_frame": "week",
        "style": "neutral",
        "context_size": 10
    }
    
    response = client.post("/api/generation", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "generated_news" in data
    assert len(data["generated_news"]) > 0
    assert "time_frame" in data
    assert data["time_frame"] == "week"


@patch("app.services.llm_service.LLMService.list_available_models")
def test_get_available_models(mock_list_models, client):
    mock_list_models.return_value = ["llama3", "mistral", "phi3"]
    
    response = client.get("/api/generation/models")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 3
    assert "llama3" in data
    assert "mistral" in data
    assert "phi3" in data
