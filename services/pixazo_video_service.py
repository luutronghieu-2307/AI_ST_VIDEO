"""
pixazo_video_service.py – Gọi Pixazo LTX 2.5 text-to-video API.

Luồng: submit job (202 QUEUED) → polling status (interval tăng dần) → trả video URL.
KHÔNG dùng image_url (text-to-video) và KHÔNG dùng webhook (app chạy local).
"""
import time
from typing import Any, Dict, Optional

import requests
from fastapi import HTTPException

from core.config import settings


class PixazoVideoService:
    """Service gọi Pixazo LTX 2.5 text-to-video."""

    @staticmethod
    def _build_headers() -> Dict[str, str]:
        """Build headers với API key. Raise 400 nếu chưa cấu hình."""
        api_key = settings.PIXAZO_API_KEY
        if not api_key or api_key == "YOUR_SUBSCRIPTION_KEY":
            raise HTTPException(400, detail="Chưa cấu hình PIXAZO_API_KEY.")
        return {
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": api_key,
        }

    @staticmethod
    def _handle_error(response: requests.Response) -> None:
        """Chuyển lỗi HTTP từ Pixazo thành HTTPException thân thiện."""
        if response.status_code == 401:
            raise HTTPException(401, detail="Pixazo API Key không hợp lệ.")
        if response.status_code == 402:
            raise HTTPException(402, detail="Hết số dư ví Pixazo. Vui lòng nạp thêm.")
        if response.status_code == 403:
            raise HTTPException(403, detail="Không có quyền truy cập Pixazo.")
        if response.status_code == 429:
            raise HTTPException(429, detail="Pixazo rate limit. Thử lại sau.")
        raise HTTPException(
            response.status_code,
            detail=f"Lỗi Pixazo: {response.text[:200]}",
        )

    @staticmethod
    def submit_video_job(
        prompt: str,
        aspect: str = "16:9",
        num_frames: int = 121,
        frame_rate: int = 16,
        seed: Optional[int] = None,
        negative: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Submit job tạo video tới Pixazo LTX 2.5.

        Returns:
            Dict: {request_id, status, polling_url}

        Raises:
            HTTPException: 400/401/402/403/429/500/504
        """
        headers = PixazoVideoService._build_headers()
        body: Dict[str, Any] = {
            "prompt": prompt,
            "aspect": aspect,
            "num_frames": num_frames,
            "frame_rate": frame_rate,
            "negative": negative or settings.VIDEO_DEFAULT_NEGATIVE,
        }
        if seed is not None:
            body["seed"] = seed

        try:
            resp = requests.post(
                settings.PIXAZO_VIDEO_GATEWAY_URL,
                json=body,
                headers=headers,
                timeout=settings.VIDEO_REQUEST_TIMEOUT,
            )
        except requests.exceptions.Timeout:
            raise HTTPException(504, detail="Pixazo timeout khi submit job.")
        except requests.exceptions.RequestException as e:
            raise HTTPException(500, detail=f"Lỗi kết nối Pixazo: {str(e)}")

        if resp.status_code not in (200, 202):
            PixazoVideoService._handle_error(resp)

        return resp.json()

    @staticmethod
    def poll_status(request_id: str) -> Dict[str, Any]:
        """
        Poll trạng thái job từ Pixazo.

        Returns:
            Dict: {status, output, error}

        Raises:
            HTTPException: 401/404/429/500/504
        """
        headers = PixazoVideoService._build_headers()
        url = f"{settings.PIXAZO_STATUS_URL}/{request_id}"

        try:
            resp = requests.get(
                url, headers=headers, timeout=settings.VIDEO_REQUEST_TIMEOUT
            )
        except requests.exceptions.Timeout:
            raise HTTPException(504, detail="Pixazo timeout khi poll status.")
        except requests.exceptions.RequestException as e:
            raise HTTPException(500, detail=f"Lỗi kết nối Pixazo: {str(e)}")

        if resp.status_code != 200:
            PixazoVideoService._handle_error(resp)

        return resp.json()

    @staticmethod
    def wait_for_completion(request_id: str) -> Dict[str, Any]:
        """
        Polling loop với interval tăng dần cho đến khi hoàn thành.

        Interval: 5s → 10s → 15s → 20s (giữ 20s). Max attempts: 90 (~30 phút).

        Raises:
            HTTPException(504): Nếu timeout.
            HTTPException(500): Nếu FAILED/ERROR.
        """
        interval = settings.VIDEO_POLL_INTERVAL_START
        max_interval = settings.VIDEO_POLL_INTERVAL_MAX
        max_attempts = settings.VIDEO_POLL_MAX_ATTEMPTS

        for _ in range(max_attempts):
            result = PixazoVideoService.poll_status(request_id)
            status = result.get("status")

            if status == "COMPLETED":
                return result
            if status in ("FAILED", "ERROR"):
                raise HTTPException(
                    500, detail=result.get("error") or "Video generation failed."
                )

            time.sleep(interval)
            interval = min(interval + 5, max_interval)

        raise HTTPException(504, detail="Timeout chờ video hoàn thành.")

    @staticmethod
    def generate_video(prompt: str, **kwargs: Any) -> str:
        """
        Wrapper: submit job + chờ hoàn thành → trả video URL.

        Returns:
            str: URL video từ Pixazo R2 CDN.
        """
        job = PixazoVideoService.submit_video_job(prompt, **kwargs)
        request_id = job.get("request_id")
        if not request_id:
            raise HTTPException(500, detail="Pixazo không trả về request_id.")

        result = PixazoVideoService.wait_for_completion(request_id)
        media_urls = result.get("output", {}).get("media_url", [])
        if not media_urls:
            raise HTTPException(500, detail="Pixazo không trả về URL video.")

        return media_urls[0]


pixazo_video_service = PixazoVideoService()
