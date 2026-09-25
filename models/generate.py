from typing import Optional
from pydantic import BaseModel, Field

class GenerateRequest(BaseModel):
    """Schema dữ liệu đầu vào cho yêu cầu tạo ảnh/logo"""
    prompt: str = Field(..., description="Mô tả chi tiết logo hoặc hình ảnh cần tạo")
    num_steps: int = Field(default=4, ge=1, le=10, description="Số bước lấy mẫu của mô hình Flux.1 (1-10)")
    seed: Optional[int] = Field(default=15, description="Seed khởi tạo để tái lập kết quả")
    height: int = Field(default=512, ge=256, le=1024, description="Chiều cao ảnh đầu ra")
    width: int = Field(default=512, ge=256, le=1024, description="Chiều rộng ảnh đầu ra")

class GenerateResponse(BaseModel):
    """Schema phản hồi kết quả tạo ảnh"""
    output: str = Field(..., description="URL công khai của ảnh đã được sinh ra")
    status: str = Field(default="success", description="Trạng thái phản hồi")
