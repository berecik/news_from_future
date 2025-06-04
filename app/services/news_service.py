import json
import logging
import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

import httpx
from fastapi import Depends

from app.config import settings
from app.models.news import NewsItem

logger = logging.getLogger(__name__)


class NewsService:
    def __init__(self):
        self.api_key = settings.NEWSDATA_API_KEY
        self.api_base_url = "https://newsdata.io/api/1"
        self.news_cache: List[NewsItem] = []
        self.categories = settings.NEWS_CATEGORIES.split(",")
        self.sources = settings.NEWS_SOURCES.split(",")
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(settings.NEWS_STORAGE_FILE), exist_ok=True)
        
        # Load cached news if available
        self._load_cache()
    
    async def fetch_news(self) -> List[NewsItem]:
        """Fetch news from NewsData.io and update cache"""
        logger.info("Fetching news from NewsData.io...")
        
        news_items = []
        
        # Create HTTP client
        async with httpx.AsyncClient() as client:
            # Fetch by category
            for category in self.categories:
                try:
                    params = {
                        "apikey": self.api_key,
                        "language": "en",
                        "category": category,
                    }
                    response = await client.get(f"{self.api_base_url}/news", params=params)
                    response.raise_for_status()
                    data = response.json()
                    news_items.extend(self._parse_news_items(data, category))
                except Exception as e:
                    logger.error(f"Error fetching news for category {category}: {e}")
            
            # Fetch by sources if needed
            if self.sources and self.sources[0]:  # Only if sources are specified
                try:
                    params = {
                        "apikey": self.api_key,
                        "language": "en",
                        "domain": ",".join(self.sources),  # NewsData.io uses domains instead of source IDs
                    }
                    response = await client.get(f"{self.api_base_url}/news", params=params)
                    response.raise_for_status()
                    data = response.json()
                    news_items.extend(self._parse_news_items(data))
                except Exception as e:
                    logger.error(f"Error fetching news for sources: {e}")
        
        # Deduplicate by title
        unique_news = {}
        for item in news_items:
            if item.title not in unique_news:
                unique_news[item.title] = item
        
        self.news_cache = list(unique_news.values())
        logger.info(f"Fetched {len(self.news_cache)} unique news items")
        
        # Save to cache file
        self._save_cache()
        
        return self.news_cache
    
    def _parse_news_items(self, api_response: Dict[str, Any], default_category: str = None) -> List[NewsItem]:
        """Parse NewsData.io response into NewsItem objects"""
        news_items = []
        
        for article in api_response.get("results", []):
            try:
                # Generate a unique ID
                article_id = f"newsdata-{hash(article.get('title', ''))}"
                
                # Parse the published date
                published_str = article.get("pubDate")
                if published_str:
                    try:
                        published_at = datetime.fromisoformat(published_str.replace("Z", "+00:00"))
                    except ValueError:
                        published_at = datetime.now()
                else:
                    published_at = datetime.now()
                
                # Get category from response or set default
                category = article.get("category", [default_category])[0] if article.get("category") else default_category
                
                # Extract custom category from url or default to provided category
                if not category:
                    for cat in self.categories:
                        if cat.lower() in article.get("link", "").lower() or cat.lower() in article.get("title", "").lower():
                            category = cat
                            break
                
                news_items.append(
                    NewsItem(
                        id=article_id,
                        title=article.get("title", ""),
                        description=article.get("description"),
                        content=article.get("content"),
                        url=article.get("link", ""),
                        image_url=article.get("image_url"),
                        source=article.get("source_id", "Unknown"),
                        category=category,
                        author=article.get("creator", ["Unknown"])[0] if article.get("creator") else "Unknown",
                        published_at=published_at,
                    )
                )
            except Exception as e:
                logger.error(f"Error parsing news item: {e}")
        
        return news_items
    
    async def get_news(
        self, 
        category: Optional[str] = None,
        source: Optional[str] = None,
        limit: int = 10,
        skip: int = 0,
    ) -> List[NewsItem]:
        """Get news from cache with optional filtering"""
        # If cache is empty, fetch news
        if not self.news_cache:
            await self.fetch_news()
        
        filtered_news = self.news_cache
        
        # Apply filters
        if category:
            filtered_news = [item for item in filtered_news if item.category == category]
        
        if source:
            filtered_news = [item for item in filtered_news if item.source == source]
        
        # Sort by published date (newest first)
        filtered_news.sort(key=lambda x: x.published_at, reverse=True)
        
        # Apply pagination
        return filtered_news[skip:skip + limit]
    
    async def get_categories(self) -> List[str]:
        """Get available news categories"""
        return self.categories
    
    async def get_sources(self) -> List[str]:
        """Get available news sources"""
        # Get unique sources from cache
        sources = set(item.source for item in self.news_cache)
        return list(sources)
    
    async def get_available_categories(self) -> List[str]:
        """Get available NewsData.io categories"""
        return [
            "business", "entertainment", "environment", "food", "health", 
            "politics", "science", "sports", "technology", "top", "world"
        ]
    
    def _save_cache(self):
        """Save news cache to file"""
        try:
            with open(settings.NEWS_STORAGE_FILE, "w") as f:
                json.dump(
                    [item.model_dump() for item in self.news_cache],
                    f,
                    default=str,
                )
        except Exception as e:
            logger.error(f"Error saving news cache: {e}")
    
    def _load_cache(self):
        """Load news cache from file"""
        try:
            if os.path.exists(settings.NEWS_STORAGE_FILE):
                with open(settings.NEWS_STORAGE_FILE, "r") as f:
                    data = json.load(f)
                    
                    # Convert string dates back to datetime
                    for item in data:
                        if isinstance(item["published_at"], str):
                            try:
                                item["published_at"] = datetime.fromisoformat(
                                    item["published_at"].replace("Z", "+00:00")
                                )
                            except ValueError:
                                item["published_at"] = datetime.now()
                    
                    self.news_cache = [NewsItem(**item) for item in data]
                    logger.info(f"Loaded {len(self.news_cache)} news items from cache")
        except Exception as e:
            logger.error(f"Error loading news cache: {e}")
            self.news_cache = []


# Dependency
def get_news_service() -> NewsService:
    return NewsService()
