# core/config.py

## Mục đích
Quản lý toàn bộ cấu hình và biến môi trường của ứng dụng thông qua class `Settings`.

## Class & Exports
- **`Settings`** – class chứa tất cả config, load từ `.env` bằng `python-dotenv`
- **`settings`** – singleton instance dùng ở toàn bộ project

## Các thuộc tính quan trọng
| Thuộc tính | Mặc định | Nguồn |
|---|---|---|
| `PROJECT_NAME` | `"AURA AI Logo Generator"` | hardcoded |
| `VERSION` | `"1.0.0"` | hardcoded |
| `HOST` | `"0.0.0.0"` | env `HOST` |
| `PORT` | `8000` | env `PORT` |
| `GROQ_API_KEY` | `""` | env `GROQ_API_KEY` |
| `GROQ_MODEL` | `"qwen/qwen3.8-27b"` | env `GROQ_MODEL` |
| `GROQ_CREATIVE_MODEL` | `"openai/gpt-oss-120b"` | env `GROQ_CREATIVE_MODEL` |
| `GROQ_TIMEOUT` | `30` giây | env `GROQ_TIMEOUT` |
| `PROMPT_TEMPLATES_FILE` | `"data/prompt_templates.json"` | env `PROMPT_TEMPLATES_FILE` |
| `GITHUB_TOKEN` | `""` | env `GITHUB_TOKEN` |
| `GITHUB_REPO` | `""` | env `GITHUB_REPO` (định dạng `owner/repo`) |
| `GITHUB_KEYS_PATH` | `"keys.json"` | env `GITHUB_KEYS_PATH` |
| `GITHUB_API_TIMEOUT` | `15` giây | env `GITHUB_API_TIMEOUT` |
| `GITHUB_API_BASE` | `"https://api.github.com"` | env `GITHUB_API_BASE` |

### Storyboard Video Config
| Thuộc tính | Mặc định | Nguồn |
|---|---|---|
| `PIXAZO_VIDEO_GATEWAY_URL` | `"https://gateway.pixazo.ai/ltx-video/v1/text-to-video"` | env |
| `PIXAZO_STATUS_URL` | `"https://gateway.pixazo.ai/v2/requests/status"` | env |
| `VIDEO_REQUEST_TIMEOUT` | `180` giây | env |
| `VIDEO_POLL_INTERVAL_START` | `5` giây | env |
| `VIDEO_POLL_INTERVAL_MAX` | `20` giây | env |
| `VIDEO_POLL_MAX_ATTEMPTS` | `90` | env |
| `VIDEO_MAX_RETRY` | `3` | env |
| `STORYBOARD_DIR` | `"data/storyboards"` | env |
| `MAX_SEGMENTS_PER_REQUEST` | `15` | env |
| `MAX_STORYBOARDS` | `50` | env |
| `STORYBOARD_RATE_LIMIT` | `50` req/phút | env |
| `VIDEO_DEFAULT_NUM_FRAMES` | `121` | env |
| `VIDEO_DEFAULT_FRAME_RATE` | `16` | env |
| `VIDEO_DEFAULT_ASPECT` | `"16:9"` | env |
| `VIDEO_DEFAULT_STYLE` | `"documentary, realistic"` | env |
| `VIDEO_DEFAULT_NEGATIVE` | `"blurry, low quality, distorted..."` | env |
| `AUDIO_MAX_FILE_SIZE` | `50MB` | env |
| `AUDIO_ALLOWED_TYPES` | `["audio/mpeg", "audio/mp3"]` | hardcoded |
| `AUDIO_TEMP_DIR` | `"data/audio_temp"` | env |

## Keywords
`settings`, `config`, `env`, `API_KEY`, `PIXAZO_API_KEY`, `GROQ_API_KEY`, `GROQ_MODEL`, `GROQ_CREATIVE_MODEL`, `GROQ_TIMEOUT`, `PROMPT_TEMPLATES_FILE`, `GITHUB_TOKEN`, `GITHUB_REPO`, `GITHUB_KEYS_PATH`, `GITHUB_API_TIMEOUT`, `GITHUB_API_BASE`, `PIXAZO_VIDEO_GATEWAY_URL`, `PIXAZO_STATUS_URL`, `VIDEO_REQUEST_TIMEOUT`, `VIDEO_POLL_INTERVAL_START`, `VIDEO_POLL_INTERVAL_MAX`, `VIDEO_POLL_MAX_ATTEMPTS`, `VIDEO_MAX_RETRY`, `STORYBOARD_DIR`, `MAX_SEGMENTS_PER_REQUEST`, `MAX_STORYBOARDS`, `STORYBOARD_RATE_LIMIT`, `VIDEO_DEFAULT_NUM_FRAMES`, `VIDEO_DEFAULT_FRAME_RATE`, `VIDEO_DEFAULT_ASPECT`, `VIDEO_DEFAULT_STYLE`, `VIDEO_DEFAULT_NEGATIVE`, `AUDIO_MAX_FILE_SIZE`, `AUDIO_ALLOWED_TYPES`, `AUDIO_TEMP_DIR`, `HOST`, `PORT`, `GATEWAY_URL`, `REQUEST_TIMEOUT`, `dotenv`, `load_dotenv`, `BASE_DIR`, `get_base_dir`, `PyInstaller`, `_MEIPASS`

## Phụ thuộc
- Không phụ thuộc module nội bộ nào
- Import bởi: `services/pixazo_service.py`, `services/groq_service.py`, `services/prompt_store.py`, `services/github_key_store.py`, `services/audio_service.py`, `services/pixazo_video_service.py`, `services/storyboard_store.py`, `services/text_segmenter.py`, `routers/suggest_router.py`, `routers/storyboard_router.py`, `main.py`
