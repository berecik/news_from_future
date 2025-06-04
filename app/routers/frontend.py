from fastapi import APIRouter, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
import os
from pathlib import Path

router = APIRouter()

# Get the directory of the current file
BASE_DIR = Path(__file__).resolve().parent.parent.parent
STATIC_DIR = BASE_DIR / "static"

# Create static directory if it doesn't exist
if not STATIC_DIR.exists():
    STATIC_DIR.mkdir(parents=True)

@router.get("/", response_class=HTMLResponse)
async def get_favicon():
    """
    Serve the favicon
    """
    return FileResponse(STATIC_DIR / "index.html")

@router.get("/favicon.ico", include_in_schema=False)
async def get_favicon():
    """
    Serve the favicon
    """
    return FileResponse(STATIC_DIR / "favicon.ico")

@router.get("/portal", response_class=HTMLResponse)
async def portal_redirect():
    """
    Secret portal entrance - redirects to the root path
    """
    return RedirectResponse(url="/")

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_redirect():
    """
    Dashboard redirect - ensures old links still work
    """
    return RedirectResponse(url="/")
