# services/pixazo_video_service.py

## Mục đích
Gọi Pixazo LTX 2.5 text-to-video API: submit job, polling, trả video URL.

## Class & Exports
- **`PixazoVideoService`** – class với static methods
- **`pixazo_video_service`** – singleton

## Methods
### `submit_video_job(prompt, aspect, num_frames, frame_rate, seed, negative) -> Dict`
- POST tới `settings.PIXAZO_VIDEO_GATEWAY_URL`
- Trả `{request_id, status, polling_url}`
- KHÔNG có `image_url` (text-to-video)

### `poll_status(request_id) -> Dict`
- GET `{settings.PIXAZO_STATUS_URL}/{request_id}`

### `wait_for_completion(request_id) -> Dict`
- Polling interval tăng dần: 5s → 10s → 15s → 20s
- Max 90 lần (~30 phút)

### `generate_video(prompt, **kwargs) -> str`
- Wrapper: submit + wait → video URL

## Xử lý lỗi
| Code | Ý nghĩa |
|---|---|
| 401 | API key sai |
| 402 | Hết số dư ví |
| 403 | Không có quyền |
| 429 | Rate limit |
| 504 | Timeout |

## Keywords
`pixazo_video_service`, `submit_video_job`, `poll_status`, `wait_for_completion`, `generate_video`, `LTX 2.5`, `text-to-video`, `request_id`, `polling_url`, `media_url`, `Ocp-Apim-Subscription-Key`, `402`, `Insufficient Balance`

## Phụ thuộc
- Import: `core.config.settings`
- Import bởi: `services/storyboard_orchestrator.py`
- Test: `test/test_pixazo_video_service.py`
