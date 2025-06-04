import logging
import json
from typing import List, Optional, Generator, Any, Dict

import httpx
import ollama
from fastapi import Depends

from app.config import settings
from app.models.news import NewsItem
from app.models.generation import TimeFrame, NewsStyle, GeneratedNewsItem
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.default_model = settings.OLLAMA_MODEL
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=60.0)
    
    async def list_available_models(self) -> List[str]:
        """List available models from Ollama"""
        try:
            response = await self.client.get("/api/tags")
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return [self.default_model]
    
    def _create_prompt(
        self,
        news_items: List[NewsItem],
        time_frame: TimeFrame,
        style: NewsStyle,
    ) -> str:
        """Create prompt for LLM based on news items"""
        # Format the current news into a context string
        news_context = "\n\n".join([
            f"TITLE: {item.title}\n"
            f"SOURCE: {item.source}\n"
            f"DATE: {item.published_at.strftime('%Y-%m-%d')}\n"
            f"CATEGORY: {item.category or 'General'}\n"
            f"CONTENT: {item.content or item.description or 'No content available'}"
            for item in news_items
        ])
        
        # Determine the future date based on time frame
        future_date = datetime.now()
        if time_frame == TimeFrame.DAY:
            future_date += timedelta(days=1)
        elif time_frame == TimeFrame.WEEK:
            future_date += timedelta(weeks=1)
        elif time_frame == TimeFrame.MONTH:
            future_date += timedelta(days=30)
        elif time_frame == TimeFrame.YEAR:
            future_date += timedelta(days=365)
        
        future_date_str = future_date.strftime("%Y-%m-%d")
        
        # Style descriptions for the prompt
        style_descriptions = {
            NewsStyle.NEUTRAL: "balanced and factual",
            NewsStyle.OPTIMISTIC: "positive and hopeful",
            NewsStyle.PESSIMISTIC: "cautious and concerned",
            NewsStyle.SENSATIONAL: "dramatic and attention-grabbing",
            NewsStyle.ANALYTICAL: "thoughtful and detailed analysis",
        }
        
        # Build the prompt
        prompt = f"""
You are a future news prediction service. Based on current news, generate 3 plausible future news articles 
that could appear on {future_date_str} ({time_frame.value} from now).

Make the articles realistic, coherent, and a logical progression from the current news.
The tone should be {style_descriptions[style]}.

Current news context:
{news_context}

Generate 3 future news articles in JSON format:
[
  {{
    "title": "Headline of the first future article",
    "content": "Detailed content of the article with at least 200 words",
    "predicted_date": "{future_date_str}",
    "source": "Name of a plausible news source",
    "category": "Category of the news"
  }},
  ... (2 more articles)
]

Make sure to only output valid JSON that can be parsed. The articles should feel like real news coverage.
"""
        return prompt
    
    async def generate_future_news(
        self,
        news_items: List[NewsItem],
        time_frame: TimeFrame = TimeFrame.WEEK,
        style: NewsStyle = NewsStyle.NEUTRAL,
        model: Optional[str] = None,
    ) -> List[GeneratedNewsItem]:
        """Generate future news based on current news"""
        model_name = model or self.default_model
        prompt = self._create_prompt(news_items, time_frame, style)
        
        try:
            # Make the generation request to Ollama
            response = await self.client.post(
                "/api/generate",
                json={
                    "model": model_name,
                    "prompt": prompt,
                    "system": "You are a future news prediction AI that creates plausible future news articles based on current events.",
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                    }
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Error from Ollama API: {response.text}")
                raise Exception(f"Failed to generate news: {response.status_code}")
            
            result = response.json()
            generated_text = result.get("response", "")
            
            # Extract JSON from the response
            try:
                # Find JSON array in the text
                json_start = generated_text.find("[")
                json_end = generated_text.rfind("]") + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = generated_text[json_start:json_end]
                    articles = json.loads(json_str)
                    
                    # Convert to model objects
                    return [
                        GeneratedNewsItem(
                            title=article["title"],
                            content=article["content"],
                            predicted_date=datetime.fromisoformat(article["predicted_date"]),
                            source=article["source"],
                            category=article.get("category"),
                        )
                        for article in articles
                    ]
                else:
                    # Fallback if we can't extract JSON
                    logger.warning("Could not extract JSON from LLM response, returning raw text")
                    return [
                        GeneratedNewsItem(
                            title="Generated Future News",
                            content=generated_text,
                            predicted_date=datetime.now() + timedelta(days=7),
                            source="AI News Generator",
                            category="General",
                        )
                    ]
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON from LLM response: {e}")
                return [
                    GeneratedNewsItem(
                        title="Error in Future News Generation",
                        content=f"Could not parse generated content: {generated_text[:500]}...",
                        predicted_date=datetime.now() + timedelta(days=7),
                        source="AI News Generator",
                        category="Error",
                    )
                ]
        except Exception as e:
            logger.error(f"Error generating future news: {e}")
            raise
    
    async def stream_future_news(
        self,
        news_items: List[NewsItem],
        time_frame: TimeFrame = TimeFrame.WEEK,
        style: NewsStyle = NewsStyle.NEUTRAL,
        model: Optional[str] = None,
    ) -> Generator[str, Any, None]:
        """Stream future news generation"""
        model_name = model or self.default_model
        prompt = self._create_prompt(news_items, time_frame, style)
        
        async with httpx.AsyncClient(timeout=None) as client:
            with client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json={
                    "model": model_name,
                    "prompt": prompt,
                    "stream": True,
                    "system": "You are a future news prediction AI that creates plausible future news articles based on current events.",
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                    }
                }
            ) as response:
                async for chunk in response.aiter_text():
                    try:
                        if chunk.strip():
                            data = json.loads(chunk)
                            if "response" in data:
                                yield data["response"]
                    except json.JSONDecodeError:
                        # Skip malformed chunks
                        continue


# Dependency
def get_llm_service() -> LLMService:
    return LLMService()
