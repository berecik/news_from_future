import json
import logging
import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

import httpx
from fastapi import Depends
from newsapi import NewsApiClient

from app.config import settings
from app.models.news import NewsItem

logger = logging.getLogger(__name__)


class NewsService:
    def __init__(self):
        self.api_key = settings.NEWSAPI_API_KEY
        self.newsapi = NewsApiClient(api_key=self.api_key)
        self.news_cache: List[NewsItem] = []
        self.categories = settings.NEWS_CATEGORIES.split(",")
        self.sources = settings.NEWS_SOURCES.split(",")
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(settings.NEWS_STORAGE_FILE), exist_ok=True)
        
        # Load cached news if available
        self._load_cache()
    
    async def fetch_news(self) -> List[NewsItem]:
        """Fetch news from NewsAPI and update cache"""
        logger.info("Fetching news from NewsAPI...")
        
        news_items = []
        
        # Fetch by top headlines from sources
        for source in self.sources:
            try:
                top_headlines = self.newsapi.get_top_headlines(sources=source, language='en')
                news_items.extend(self._parse_news_items(top_headlines))
            except Exception as e:
                logger.error(f"Error fetching top headlines for source {source}: {e}")
        
        # Fetch by category
        for category in self.categories:
            try:
                category_news = self.newsapi.get_top_headlines(category=category, language='en')
                news_items.extend(self._parse_news_items(category_news))
            except Exception as e:
                logger.error(f"Error fetching news for category {category}: {e}")
        
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
    
    def _parse_news_items(self, api_response: Dict[str, Any]) -> List[NewsItem]:
        """Parse NewsAPI response into NewsItem objects"""
        news_items = []
        
        for article in api_response.get("articles", []):
            try:
                # Generate a unique ID
                article_id = f"{article.get('source', {}).get('id', 'unknown')}-{hash(article.get('title', ''))}"
                
                # Parse the published date
                published_str = article.get("publishedAt")
                if published_str:
                    published_at = datetime.fromisoformat(published_str.replace("Z", "+00:00"))
                else:
                    published_at = datetime.now()
                
                # Extract category from url or default to unknown
                category = None
                for cat in self.categories:
                    if cat.lower() in article.get("url", "").lower() or cat.lower() in article.get("title", "").lower():
                        category = cat
                        break
                
                news_items.append(
                    NewsItem(
                        id=article_id,
                        title=article.get("title", ""),
                        description=article.get("description"),
                        content=article.get("content"),
                        url=article.get("url", ""),
                        image_url=article.get("urlToImage"),
                        source=article.get("source", {}).get("name", "Unknown"),
                        category=category,
                        author=article.get("author"),
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
        return [item.source for item in self.news_cache]
    
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
