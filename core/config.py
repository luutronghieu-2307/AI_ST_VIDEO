import os
import sys
from dotenv import load_dotenv

# Load các biến môi trường từ .env
load_dotenv()

def get_base_dir() -> str:
    """Trả về thư mục gốc thực tế của ứng dụng (kể cả khi chạy bundle PyInstaller)."""
    if getattr(sys, 'frozen', False):
        if hasattr(sys, '_MEIPASS'):
            return sys._MEIPASS
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BASE_DIR = get_base_dir()

class Settings:
    PROJECT_NAME: str = "AURA AI Logo Generator"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Backend API tạo logo và hình ảnh sử dụng Flux.1 Schnell qua Pixazo Gateway"
    
    BASE_DIR: str = BASE_DIR

    # Server config
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Pixazo Gateway Config
    PIXAZO_API_KEY: str = os.getenv("PIXAZO_API_KEY", "")
    PIXAZO_GATEWAY_URL: str = os.getenv(
        "PIXAZO_GATEWAY_URL", 
        "https://gateway.pixazo.ai/flux-1-schnell/v1/getData"
    )
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "60"))

    # Groq LLM Config
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
    GROQ_CREATIVE_MODEL: str = os.getenv("GROQ_CREATIVE_MODEL", "openai/gpt-oss-120b")
    GROQ_TIMEOUT: int = int(os.getenv("GROQ_TIMEOUT", "30"))

    # Prompt Templates Storage
    PROMPT_TEMPLATES_FILE: str = os.getenv(
        "PROMPT_TEMPLATES_FILE",
        os.path.join(BASE_DIR, "data", "prompt_templates.json")
    )

    # GitHub License Key Store (remote key management)
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    GITHUB_REPO: str = os.getenv("GITHUB_REPO", "")
    GITHUB_KEYS_PATH: str = os.getenv("GITHUB_KEYS_PATH", "keys.json")
    GITHUB_API_TIMEOUT: int = int(os.getenv("GITHUB_API_TIMEOUT", "15"))
    GITHUB_API_BASE: str = os.getenv("GITHUB_API_BASE", "https://api.github.com")

    # ── Storyboard Video Config ──────────────────────────────────────────
    # Pixazo LTX 2.5 Gateway (text-to-video)
    PIXAZO_VIDEO_GATEWAY_URL: str = os.getenv(
        "PIXAZO_VIDEO_GATEWAY_URL",
        "https://gateway.pixazo.ai/ltx-video/v1/text-to-video"
    )
    PIXAZO_STATUS_URL: str = os.getenv(
        "PIXAZO_STATUS_URL",
        "https://gateway.pixazo.ai/v2/requests/status"
    )
    VIDEO_REQUEST_TIMEOUT: int = int(os.getenv("VIDEO_REQUEST_TIMEOUT", "180"))
    VIDEO_POLL_INTERVAL_START: int = int(os.getenv("VIDEO_POLL_INTERVAL_START", "5"))
    VIDEO_POLL_INTERVAL_MAX: int = int(os.getenv("VIDEO_POLL_INTERVAL_MAX", "20"))
    VIDEO_POLL_MAX_ATTEMPTS: int = int(os.getenv("VIDEO_POLL_MAX_ATTEMPTS", "90"))
    VIDEO_MAX_RETRY: int = int(os.getenv("VIDEO_MAX_RETRY", "3"))

    # Storyboard Storage
    STORYBOARD_DIR: str = os.getenv(
        "STORYBOARD_DIR",
        os.path.join(BASE_DIR, "data", "storyboards")
    )
    MAX_SEGMENTS_PER_REQUEST: int = int(os.getenv("MAX_SEGMENTS_PER_REQUEST", "15"))
    MAX_STORYBOARDS: int = int(os.getenv("MAX_STORYBOARDS", "50"))
    STORYBOARD_RATE_LIMIT: int = int(os.getenv("STORYBOARD_RATE_LIMIT", "50"))

    # Video Defaults
    VIDEO_DEFAULT_NUM_FRAMES: int = int(os.getenv("VIDEO_DEFAULT_NUM_FRAMES", "121"))
    VIDEO_DEFAULT_FRAME_RATE: int = int(os.getenv("VIDEO_DEFAULT_FRAME_RATE", "16"))
    VIDEO_DEFAULT_ASPECT: str = os.getenv("VIDEO_DEFAULT_ASPECT", "16:9")
    VIDEO_DEFAULT_STYLE: str = os.getenv("VIDEO_DEFAULT_STYLE", "documentary, realistic")
    VIDEO_DEFAULT_NEGATIVE: str = os.getenv(
        "VIDEO_DEFAULT_NEGATIVE",
        "blurry, low quality, distorted, worst quality, jpeg artifacts"
    )

    # Audio Upload Config
    AUDIO_MAX_FILE_SIZE: int = int(os.getenv("AUDIO_MAX_FILE_SIZE", str(50 * 1024 * 1024)))
    AUDIO_ALLOWED_TYPES: list = ["audio/mpeg", "audio/mp3"]
    AUDIO_TEMP_DIR: str = os.getenv(
        "AUDIO_TEMP_DIR",
        os.path.join(BASE_DIR, "data", "audio_temp")
    )

settings = Settings()

