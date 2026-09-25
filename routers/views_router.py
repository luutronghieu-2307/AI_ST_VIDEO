import os
from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from core.config import settings

views_router = APIRouter(tags=["Frontend Views"])

TEMPLATES_DIR = os.path.join(settings.BASE_DIR, "templates")
if not os.path.exists(TEMPLATES_DIR):
    TEMPLATES_DIR = "templates"

templates = Jinja2Templates(directory=TEMPLATES_DIR)

@views_router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def serve_index(request: Request):
    """Render trang chủ Frontend thông qua Jinja2 Template Engine"""
    index_file = os.path.join(TEMPLATES_DIR, "index.html")
    if not os.path.exists(index_file):
        raise HTTPException(
            status_code=404, 
            detail=f"Template 'index.html' không tồn tại tại {TEMPLATES_DIR}"
        )
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"title": "AURA AI Logo Generator"}
    )
