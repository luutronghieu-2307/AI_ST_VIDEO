import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from core.config import settings
from routers.views_router import views_router
from routers.generate_router import generate_router
from routers.suggest_router import suggest_router
from routers.storyboard_router import storyboard_router
from services.storyboard_orchestrator import cleanup_stuck_segments

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    )

# Phục vụ static assets (css, js, images)
css_dir = os.path.join(settings.BASE_DIR, "templates", "css")
if os.path.exists(css_dir):
    app.mount("/css", StaticFiles(directory=css_dir), name="css")

js_dir = os.path.join(settings.BASE_DIR, "templates", "js")
if os.path.exists(js_dir):
    app.mount("/js", StaticFiles(directory=js_dir), name="js")

icon_dir = os.path.join(settings.BASE_DIR, "ICON")
if os.path.exists(icon_dir):
    app.mount("/icon", StaticFiles(directory=icon_dir), name="icon")

templates_dir = os.path.join(settings.BASE_DIR, "templates")
if os.path.exists(templates_dir):
    app.mount("/templates", StaticFiles(directory=templates_dir), name="templates")

# Phục vụ file video ghép nối
merged_videos_dir = os.path.join(settings.BASE_DIR, "data", "merged_videos")
os.makedirs(merged_videos_dir, exist_ok=True)
app.mount("/static/merged_videos", StaticFiles(directory=merged_videos_dir), name="merged_videos")

# Đăng ký các router
app.include_router(views_router)
app.include_router(generate_router)
app.include_router(suggest_router)
app.include_router(storyboard_router)


@app.on_event("startup")
async def startup_cleanup():
    """Cleanup segment treo khi server khởi động."""
    try:
        cleaned = cleanup_stuck_segments()
        if cleaned > 0:
            print(f"🧹 Đã cleanup {cleaned} segment bị treo.")
    except Exception as e:
        print(f"⚠️ Lỗi cleanup startup: {e}")


if __name__ == "__main__":
    print(f"🚀 Server đang khởi chạy tại http://{settings.HOST}:{settings.PORT}")
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=False)
