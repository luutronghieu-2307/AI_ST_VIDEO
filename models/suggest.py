from typing import Optional
from pydantic import BaseModel, Field


class SuggestRequest(BaseModel):
    """Schema đầu vào để yêu cầu Groq LLM phân tích ảnh và sinh prompt"""
    image_base64: str = Field(..., description="Ảnh mẫu đã encode base64")
    image_mime: str = Field(default="image/jpeg", description="MIME type: image/jpeg, image/png, image/webp")
    prompt_name: str = Field(..., min_length=1, max_length=80, description="Tên định danh cho prompt này")
    groq_api_key: Optional[str] = Field(default=None, description="Groq API Key từ phía client (ưu tiên hơn .env)")
    model_id: Optional[str] = Field(default=None, description="Model ID Groq muốn sử dụng (phải là model vision)")
    mode: str = Field(default="standard", description="Chế độ sinh prompt: 'standard' (bám sát ảnh) hoặc 'advanced' (sáng tạo với GPT-120B)")


class GroqModelInfo(BaseModel):
    """Schema thông tin model Groq hỗ trợ vision"""
    id: str = Field(..., description="ID định danh của model trên Groq")
    name: str = Field(..., description="Tên hiển thị thân thiện")
    context_window: Optional[int] = Field(default=None, description="Độ dài context window")


class SuggestResponse(BaseModel):
    """Schema phản hồi sau khi LLM sinh prompt thành công"""
    prompt: str = Field(..., description="Prompt chi tiết do LLM sinh ra cho AI tạo ảnh")
    name: str = Field(..., description="Tên của prompt template vừa lưu")
    saved: bool = Field(default=True, description="Đã lưu vào prompt_templates.json")
    template_id: str = Field(..., description="ID duy nhất của template vừa tạo")
    mode: str = Field(default="standard", description="Chế độ đã thực thi ('standard' hoặc 'advanced')")


class PromptTemplate(BaseModel):
    """Schema đại diện cho một prompt template được lưu trữ"""
    id: str = Field(..., description="ID duy nhất (UUID4)")
    name: str = Field(..., description="Tên hiển thị trong dropdown")
    prompt: str = Field(..., description="Nội dung prompt đầy đủ")
    created_at: str = Field(..., description="Timestamp ISO tạo template")
    is_default: bool = Field(default=False, description="True = template mặc định, không thể xóa")


class BatchDeleteTemplateRequest(BaseModel):
    """Schema yêu cầu xóa nhiều prompt template cùng lúc"""
    ids: list[str] = Field(..., min_length=1, description="Danh sách ID các template cần xóa")
