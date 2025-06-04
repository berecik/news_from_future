import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse, HTMLResponse

from app.config import settings
from app.routers import news, generation
from app.services.scheduler import start_scheduler, shutdown_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start background tasks
    logger.info("Starting scheduler for news fetching...")
    start_scheduler()
    
    yield
    
    # Clean up resources
    logger.info("Shutting down scheduler...")
    shutdown_scheduler()


app = FastAPI(
    title="News From Future API",
    description="""
    API that fetches current news from public sources and generates future news predictions using a local LLM.
    
    ## Features
    
    * Fetch current news articles from multiple sources
    * Generate future news predictions based on current trends
    * Support for different time frames (day, week, month)
    * Support for different news styles (neutral, optimistic, pessimistic)
    * Streaming generation for real-time updates
    
    ## Notes
    
    * The API uses a local LLM through Ollama for generation
    * News data is refreshed periodically in the background
    """,
    version="0.1.0",
    lifespan=lifespan,
    docs_url=None,  # Disable automatic /docs endpoint
    redoc_url=None,  # Disable automatic /redoc endpoint
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(news.router, prefix="/api/news", tags=["news"])
app.include_router(generation.router, prefix="/api/generation", tags=["generation"])


@app.get("/", tags=["status"])
async def root():
    """
    Root endpoint returning basic service information.
    """
    return {
        "status": "online",
        "service": "News From Future API",
        "version": "0.1.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["status"])
async def health_check():
    """
    Health check endpoint for monitoring service status.
    """
    return {"status": "healthy"}


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """
    Custom Swagger UI documentation.
    """
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    """
    ReDoc documentation.
    """
    return get_redoc_html(
        openapi_url="/openapi.json",
        title=app.title + " - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
    )


@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint():
    """
    Returns the OpenAPI schema as JSON.
    """
    return JSONResponse(get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    ))
