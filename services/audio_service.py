"""
audio_service.py – Xử lý file MP3: lưu tạm, đo thời lượng, phân bổ num_frames.

MP3 là "chuẩn thời gian" cho storyboard: num_frames mỗi segment được tính
dựa trên tỷ lệ độ dài text so với tổng thời lượng MP3.
"""
import os
import uuid
from typing import List

from fastapi import HTTPException
from mutagen.mp3 import MP3
from mutagen import MutagenError

from core.config import settings

MIN_FRAMES = 25
MAX_FRAMES = 121


def save_uploaded_audio(file_bytes: bytes, filename: str) -> str:
    """
    Lưu file MP3 tạm vào data/audio_temp/.

    Args:
        file_bytes: Nội dung file
        filename: Tên file gốc

    Returns:
        str: Đường dẫn file đã lưu

    Raises:
        HTTPException(400): Nếu file quá lớn hoặc sai định dạng
        HTTPException(500): Nếu ghi file lỗi
    """
    if len(file_bytes) > settings.AUDIO_MAX_FILE_SIZE:
        max_mb = settings.AUDIO_MAX_FILE_SIZE // (1024 * 1024)
        raise HTTPException(
            status_code=400,
            detail=f"File MP3 quá lớn (tối đa {max_mb}MB).",
        )

    if not filename or not filename.lower().endswith(".mp3"):
        raise HTTPException(status_code=400, detail="Chỉ chấp nhận file MP3.")

    os.makedirs(settings.AUDIO_TEMP_DIR, exist_ok=True)

    unique_name = f"{uuid.uuid4().hex}_{filename}"
    file_path = os.path.join(settings.AUDIO_TEMP_DIR, unique_name)

    try:
        with open(file_path, "wb") as f:
            f.write(file_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi lưu file MP3: {str(e)}")

    return file_path


def get_audio_duration(file_path: str) -> float:
    """
    Đo thời lượng file MP3 (giây) bằng mutagen.

    Args:
        file_path: Đường dẫn file MP3

    Returns:
        float: Thời lượng tính bằng giây

    Raises:
        HTTPException(400): Nếu file không tồn tại hoặc hỏng
    """
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=400, detail="File MP3 không tồn tại.")

    try:
        audio = MP3(file_path)
        duration = audio.info.length
        if duration <= 0:
            raise HTTPException(
                status_code=400, detail="File MP3 có thời lượng không hợp lệ."
            )
        return float(duration)
    except MutagenError as e:
        raise HTTPException(status_code=400, detail=f"File MP3 bị hỏng: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Không đọc được file MP3: {str(e)}"
        )


def round_to_1_plus_8k(value: int) -> int:
    """
    Làm tròn về dạng 1 + 8k gần nhất (25, 33, 41... 121).

    Args:
        value: Giá trị cần làm tròn

    Returns:
        int: Giá trị đã làm tròn, clamp trong [25, 121]
    """
    k = round((value - 1) / 8)
    result = 1 + 8 * k
    return max(MIN_FRAMES, min(MAX_FRAMES, result))


def allocate_frames_to_segments(
    segments: List[str],
    total_duration: float,
    frame_rate: int = 16,
) -> List[int]:
    """
    Phân bổ num_frames cho từng segment theo tỷ lệ độ dài text.

    Công thức:
        num_frames_i = clamp(round(dur_i × frame_rate), 25, 121)
        dur_i = (len(text_i) / total_text_len) × total_duration

    Args:
        segments: Danh sách text segments
        total_duration: Tổng thời lượng MP3 (giây)
        frame_rate: FPS (mặc định 16)

    Returns:
        List[int]: Danh sách num_frames (mỗi giá trị là 1+8k)

    Raises:
        HTTPException(400): Nếu segments rỗng hoặc tổng text = 0
    """
    if not segments:
        raise HTTPException(status_code=400, detail="Danh sách segment rỗng.")

    total_text_len = sum(len(s) for s in segments)
    if total_text_len == 0:
        raise HTTPException(status_code=400, detail="Tổng độ dài text bằng 0.")

    result: List[int] = []
    for text in segments:
        ratio = len(text) / total_text_len
        segment_duration = ratio * total_duration
        raw_frames = round(segment_duration * frame_rate)
        clamped = max(MIN_FRAMES, min(MAX_FRAMES, raw_frames))
        result.append(round_to_1_plus_8k(clamped))

    return result


def cleanup_temp_audio(file_path: str) -> None:
    """
    Xóa file MP3 tạm sau khi xử lý xong.

    Không raise exception nếu file không tồn tại hoặc xóa lỗi.
    """
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
    except Exception:
        pass
