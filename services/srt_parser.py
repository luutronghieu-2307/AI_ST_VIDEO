"""
srt_parser.py – Module phân tích cú pháp phụ đề Subtitle (.srt).

Trích xuất:
  - Thứ tự (order)
  - Mốc thời gian bắt đầu & kết thúc (start_sec, end_sec, duration_sec, timecode)
  - Văn bản kịch bản (text)
  - Số khung hình chuẩn hóa theo công thức 1+8k @ 16fps (num_frames)
"""
import re
from typing import List, NamedTuple
from fastapi import HTTPException

MIN_FRAMES = 25
MAX_FRAMES = 121
DEFAULT_FPS = 16
MAX_ALLOWED_SEGMENTS = 30


class ParsedSrtSegment(NamedTuple):
    order: int
    start_sec: float
    end_sec: float
    duration_sec: float
    timecode: str
    text: str
    num_frames: int


def parse_timestamp(ts_str: str) -> float:
    """
    Chuyển đổi chuỗi timestamp SRT (HH:MM:SS,mmm hoặc HH:MM:SS.mmm) thành giây.
    Ví dụ: '00:01:23,456' -> 83.456
    """
    ts_str = ts_str.strip().replace(".", ",")
    parts = ts_str.split(":")
    if len(parts) != 3:
        raise ValueError(f"Định dạng timestamp không hợp lệ: {ts_str}")

    hours = float(parts[0])
    minutes = float(parts[1])
    sec_parts = parts[2].split(",")
    seconds = float(sec_parts[0])
    millis = float(sec_parts[1]) if len(sec_parts) > 1 else 0.0

    return round(hours * 3600 + minutes * 60 + seconds + (millis / 1000.0), 3)


def calculate_frames_1_plus_8k(
    duration_sec: float,
    fps: int = DEFAULT_FPS,
    min_frames: int = MIN_FRAMES,
    max_frames: int = MAX_FRAMES,
) -> int:
    """
    Tính số frame tương ứng với thời lượng và làm tròn về chuẩn 1 + 8k gần nhất.
    """
    raw_frames = round(duration_sec * fps)
    k = round((raw_frames - 1) / 8)
    calc_frames = 1 + 8 * k
    return max(min_frames, min(max_frames, calc_frames))


def parse_srt(
    srt_content: str,
    fps: int = DEFAULT_FPS,
    max_segments: int = MAX_ALLOWED_SEGMENTS,
    extra_padding_sec: float = 1.0,
) -> List[ParsedSrtSegment]:
    """
    Phân tích toàn bộ nội dung file/chuỗi SRT thành danh sách ParsedSrtSegment.
    Tự động cộng thêm extra_padding_sec (mặc định 1.0s) vào phân đoạn cuối cùng
    để đảm bảo tổng thời lượng video luôn dài hơn thời lượng thoại/phụ đề.

    Args:
        srt_content: Nội dung văn bản định dạng SRT.
        fps: Số khung hình trên giây (mặc định 16).
        max_segments: Số phân đoạn tối đa cho phép.
        extra_padding_sec: Số giây cộng thêm cho segment cuối (mặc định 1.0s).

    Returns:
        List[ParsedSrtSegment]

    Raises:
        HTTPException(400): Khi định dạng SRT không hợp lệ hoặc rỗng.
    """
    if not srt_content or not srt_content.strip():
        raise HTTPException(status_code=400, detail="Nội dung phụ đề SRT rỗng.")

    content = srt_content.replace("\r\n", "\n").replace("\r", "\n").strip()
    blocks = re.split(r"\n\s*\n+", content)
    time_pattern = re.compile(r"(\d{1,2}:\d{2}:\d{2}[,\.]\d{1,3})\s*-->\s*(\d{1,2}:\d{2}:\d{2}[,\.]\d{1,3})")

    parsed_items: List[ParsedSrtSegment] = []

    for block in blocks:
        lines = [line.strip() for line in block.strip().split("\n") if line.strip()]
        if not lines:
            continue

        time_match = None
        time_line_idx = -1
        for idx, line in enumerate(lines):
            m = time_pattern.search(line)
            if m:
                time_match = m
                time_line_idx = idx
                break

        if not time_match:
            continue

        start_raw, end_raw = time_match.group(1), time_match.group(2)
        text_lines = lines[time_line_idx + 1:]
        text_clean = " ".join(text_lines).strip()
        if not text_clean:
            continue

        try:
            start_sec = parse_timestamp(start_raw)
            end_sec = parse_timestamp(end_raw)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Lỗi mốc thời gian: {str(e)}")

        if end_sec <= start_sec:
            raise HTTPException(
                status_code=400,
                detail=f"Thời gian kết thúc ({end_raw}) phải lớn hơn thời gian bắt đầu ({start_raw}).",
            )

        duration_sec = round(end_sec - start_sec, 3)
        timecode = f"{start_raw} --> {end_raw}"
        num_frames = calculate_frames_1_plus_8k(duration_sec, fps=fps)

        parsed_items.append(
            ParsedSrtSegment(
                order=len(parsed_items) + 1,
                start_sec=start_sec,
                end_sec=end_sec,
                duration_sec=duration_sec,
                timecode=timecode,
                text=text_clean,
                num_frames=num_frames,
            )
        )

    if not parsed_items:
        raise HTTPException(
            status_code=400,
            detail="Không tìm thấy cấu trúc phụ đề SRT hợp lệ (cần định dạng: 00:00:00,000 --> 00:00:00,000).",
        )

    if len(parsed_items) > max_segments:
        raise HTTPException(
            status_code=400,
            detail=f"Số lượng phân đoạn phụ đề ({len(parsed_items)}) vượt quá giới hạn cho phép ({max_segments}).",
        )

    # Thêm padding thời gian vào phân đoạn cuối cùng (+1s) để video không bị hết trước audio
    if extra_padding_sec > 0 and parsed_items:
        last = parsed_items[-1]
        padded_end_sec = round(last.end_sec + extra_padding_sec, 3)
        padded_duration_sec = round(last.duration_sec + extra_padding_sec, 3)
        padded_num_frames = calculate_frames_1_plus_8k(padded_duration_sec, fps=fps)
        parsed_items[-1] = ParsedSrtSegment(
            order=last.order,
            start_sec=last.start_sec,
            end_sec=padded_end_sec,
            duration_sec=padded_duration_sec,
            timecode=last.timecode,
            text=last.text,
            num_frames=padded_num_frames,
        )

    return parsed_items

