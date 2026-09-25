import requests
from fastapi import HTTPException
from core.config import settings
from models.generate import GenerateRequest

class PixazoService:
    """Service chịu trách nhiệm tương tác trực tiếp với Pixazo Gateway"""

    @staticmethod
    def generate_image(payload: GenerateRequest) -> str:
        api_key = settings.PIXAZO_API_KEY
        
        if not api_key or api_key == "YOUR_SUBSCRIPTION_KEY":
            raise HTTPException(
                status_code=400,
                detail="Chưa cấu hình PIXAZO_API_KEY hợp lệ trong file .env hoặc biến môi trường."
            )

        headers = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "Ocp-Apim-Subscription-Key": api_key
        }

        body = {
            "prompt": payload.prompt,
            "num_steps": payload.num_steps,
            "seed": payload.seed if payload.seed is not None else 15,
            "height": payload.height,
            "width": payload.width
        }

        try:
            response = requests.post(
                settings.PIXAZO_GATEWAY_URL, 
                json=body, 
                headers=headers, 
                timeout=settings.REQUEST_TIMEOUT
            )
            
            if response.status_code != 200:
                error_data = response.json() if "application/json" in response.headers.get("content-type", "") else {}
                error_msg = error_data.get("message") or response.text or f"Status {response.status_code}"
                raise HTTPException(
                    status_code=response.status_code, 
                    detail=f"Lỗi từ Pixazo Gateway: {error_msg}"
                )

            result = response.json()
            image_url = result.get("output")
            
            if not image_url:
                raise HTTPException(
                    status_code=500, 
                    detail="Pixazo Gateway không trả về trường 'output' chứa URL ảnh."
                )

            return image_url

        except requests.exceptions.Timeout:
            raise HTTPException(
                status_code=504, 
                detail="Yêu cầu tới Pixazo Gateway bị quá hạn (Gateway Timeout)."
            )
        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Lỗi kết nối tới Pixazo Gateway: {str(e)}"
            )

pixazo_service = PixazoService()
