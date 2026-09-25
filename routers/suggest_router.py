from typing import List, Optional
from fastapi import APIRouter, Request, Query
from fastapi.responses import JSONResponse

from models.suggest import (
    SuggestRequest, SuggestResponse, PromptTemplate, 
    GroqModelInfo, BatchDeleteTemplateRequest
)
from services.groq_service import groq_service
from services.prompt_store import (
    load_templates, save_template, delete_template, delete_templates_batch
)
from services.rate_limiter import enforce_rate_limit
from core.config import settings

suggest_router = APIRouter(prefix="/api", tags=["AI Prompt Builder"])


@suggest_router.get(
    "/groq-models",
    response_model=List[GroqModelInfo],
    summary="Lấy danh sách các model Groq hỗ trợ Vision (đọc ảnh)"
)
async def get_groq_vision_models(
    groq_api_key: Optional[str] = Query(None, description="Groq API Key từ client")
):
    """Gọi Groq API để lấy danh sách model và chỉ lọc các model có khả năng vision/đọc ảnh."""
    api_key = groq_api_key or settings.GROQ_API_KEY
    return groq_service.get_vision_models(api_key=api_key)


@suggest_router.post(
    "/suggest-prompt",
    response_model=SuggestResponse,
    summary="Dùng Groq LLM phân tích ảnh và sinh prompt AI (Standard hoặc Advanced GPT-120B)"
)
async def suggest_prompt_from_image(
    payload: SuggestRequest,
    request: Request
):
    """Phân tích ảnh với Vision model và lưu vào prompt templates JSON."""
    limit = 10 if payload.mode == "advanced" else 20
    prefix = "suggest_advanced" if payload.mode == "advanced" else "suggest_standard"
    enforce_rate_limit(request, limit=limit, key_prefix=prefix)

    api_key = payload.groq_api_key or settings.GROQ_API_KEY
    generated_prompt = groq_service.suggest_prompt(
        image_base64=payload.image_base64,
        image_mime=payload.image_mime,
        api_key=api_key,
        model_id=payload.model_id,
        mode=payload.mode
    )
    saved = save_template(name=payload.prompt_name, prompt=generated_prompt)
    return SuggestResponse(
        prompt=generated_prompt,
        name=saved.name,
        saved=True,
        template_id=saved.id,
        mode=payload.mode
    )


@suggest_router.get(
    "/prompt-templates",
    response_model=List[PromptTemplate],
    summary="Lấy danh sách tất cả prompt templates đã lưu"
)
async def get_prompt_templates():
    """Trả về toàn bộ templates (mặc định + do user tạo) cho dropdown."""
    return load_templates()


@suggest_router.delete(
    "/prompt-templates/{template_id}",
    summary="Xóa một prompt template theo ID"
)
async def remove_prompt_template(template_id: str):
    """Xóa template theo ID. Template mặc định (is_default=True) không thể xóa."""
    delete_template(template_id)
    return JSONResponse(content={"success": True, "deleted_id": template_id})


@suggest_router.post(
    "/prompt-templates/batch-delete",
    summary="Xóa nhiều prompt templates cùng lúc"
)
async def remove_prompt_templates_batch(payload: BatchDeleteTemplateRequest):
    """Xóa nhiều template theo danh sách IDs (bỏ qua template mặc định)."""
    deleted = delete_templates_batch(payload.ids)
    return JSONResponse(content={
        "success": True, 
        "deleted_count": len(deleted), 
        "deleted_ids": deleted
    })

