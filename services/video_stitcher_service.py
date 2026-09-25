"""
video_stitcher_service.py – Ghép nối video phân đoạn và lồng âm thanh MP3.

Quy trình:
  1. Tải danh sách video segment (.mp4) về thư mục tạm.
  2. Dùng FFmpeg Concat Demuxer ghép các video thành 1 video liền mạch.
  3. Lồng track âm thanh MP3 (nếu có) vào video bằng FFmpeg.
  4. Lưu file kết quả vào data/merged_videos/ và dọn dẹp file tạm.
"""
import os
import shutil
import subprocess
import urllib.request
from typing import List, Optional
import imageio_ffmpeg

MERGED_VIDEOS_DIR = os.path.join("data", "merged_videos")
TEMP_SEGMENTS_DIR = os.path.join("data", "temp_segments")


def _ensure_dirs() -> None:
    os.makedirs(MERGED_VIDEOS_DIR, exist_ok=True)
    os.makedirs(TEMP_SEGMENTS_DIR, exist_ok=True)


def download_video_segment(url: str, dest_path: str, timeout: int = 60) -> str:
    """Tải 1 file video MP4 từ URL về máy."""
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "AURA-Video-Stitcher/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as response, open(dest_path, "wb") as out_file:
        shutil.copyfileobj(response, out_file)
    return dest_path


def stitch_and_mux_storyboard(
    storyboard_id: str,
    segment_urls: List[str],
    audio_path: Optional[str] = None,
) -> str:
    """
    Ghép nối các video phân đoạn và lồng tiếng MP3.

    Args:
        storyboard_id: ID của storyboard.
        segment_urls: Danh sách URL video phân đoạn (theo đúng thứ tự).
        audio_path: Đường dẫn file MP3 lồng tiếng (tùy chọn).

    Returns:
        str: Đường dẫn URL static tới video hoàn chỉnh (vd: /static/merged_videos/xyz_final.mp4)
    """
    if not segment_urls:
        raise ValueError("Danh sách URL video phân đoạn rỗng.")

    _ensure_dirs()
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    work_dir = os.path.join(TEMP_SEGMENTS_DIR, storyboard_id)
    os.makedirs(work_dir, exist_ok=True)

    downloaded_files: List[str] = []
    try:
        # Bước 1: Tải các segment về
        for idx, url in enumerate(segment_urls, start=1):
            seg_file = os.path.join(work_dir, f"segment_{idx:03d}.mp4")
            download_video_segment(url, seg_file)
            downloaded_files.append(seg_file)

        # Bước 2: Tạo concat file list
        concat_list_path = os.path.join(work_dir, "concat_list.txt")
        with open(concat_list_path, "w", encoding="utf-8") as f:
            for seg_file in downloaded_files:
                abs_seg = os.path.abspath(seg_file).replace("\\", "/")
                f.write(f"file '{abs_seg}'\n")

        temp_merged_video = os.path.join(work_dir, "temp_merged.mp4")
        final_video_filename = f"{storyboard_id}_final.mp4"
        final_output_path = os.path.join(MERGED_VIDEOS_DIR, final_video_filename)

        # Bước 3: Nối các video segment (sử dụng concat demuxer)
        concat_cmd = [
            ffmpeg_exe,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            concat_list_path,
            "-c",
            "copy",
            temp_merged_video,
        ]
        result = subprocess.run(concat_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Nếu copy stream lỗi (do keyframes/codecs khác nhau nhẹ), fallback sang re-encode
        if result.returncode != 0:
            reencode_cmd = [
                ffmpeg_exe,
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                concat_list_path,
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                temp_merged_video,
            ]
            subprocess.run(reencode_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Bước 4: Lồng tiếng MP3 (nếu có audio_path)
        if audio_path and os.path.exists(audio_path):
            mux_cmd = [
                ffmpeg_exe,
                "-y",
                "-i",
                temp_merged_video,
                "-i",
                audio_path,
                "-c:v",
                "copy",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                final_output_path,
            ]
            subprocess.run(mux_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            shutil.copyfile(temp_merged_video, final_output_path)


        return f"/static/merged_videos/{final_video_filename}"

    finally:
        # Dọn dẹp thư mục tạm của storyboard này
        try:
            if os.path.exists(work_dir):
                shutil.rmtree(work_dir)
        except Exception:
            pass
