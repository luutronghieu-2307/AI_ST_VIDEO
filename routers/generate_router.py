from fastapi import APIRouter, Depends, Request
from models.generate import GenerateRequest, GenerateResponse
from services.pixazo_service import pixazo_service
from services.rate_limiter import enforce_rate_limit

generate_router = APIRouter(prefix="/api", tags=["Image Generation"])

@generate_router.post(
    "/generate", 
    response_model=GenerateResponse,
    summary="Tạo hình ảnh hoặc Logo bằng Flux.1 Schnell"
)
async def generate_image(
    payload: GenerateRequest,
    request: Request,
    _: None = Depends(enforce_rate_limit)
):
    """
    Endpoint nhận thông tin prompt và các cấu hình kích thước, seed, step 
    để sinh ảnh qua Pixazo Gateway.
    """
    image_url = pixazo_service.generate_image(payload)
    return GenerateResponse(output=image_url, status="success")
