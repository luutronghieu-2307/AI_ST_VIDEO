# services/audio_service.py

## Mục đích
Xử lý file MP3: lưu tạm, đo thời lượng, phân bổ num_frames.

## Functions
### `save_uploaded_audio(file_bytes, filename) -> str`
- Validate size ≤ 50MB, extension .mp3
- Lưu vào `data/audio_temp/`

### `get_audio_duration(file_path) -> float`
- Đo thời lượng bằng `mutagen.mp3.MP3`

### `allocate_frames_to_segments(segments, total_duration, frame_rate=16) -> List[int]`
- Công thức: `num_frames_i = clamp(round(dur_i × frame_rate), 25, 121)`
- `dur_i = (len(text_i) / total_text_len) × total_duration`

### `round_to_1_plus_8k(value) -> int`
- Làm tròn về 25, 33, 41... 121

### `cleanup_temp_audio(file_path) -> None`
- Xóa file tạm, không raise

## Hằng số
| Hằng | Giá trị |
|---|---|
| `MIN_FRAMES` | 25 |
| `MAX_FRAMES` | 121 |

## Dependency
`mutagen>=1.47.0`

## Keywords
`audio_service`, `save_uploaded_audio`, `get_audio_duration`, `allocate_frames_to_segments`, `round_to_1_plus_8k`, `cleanup_temp_audio`, `mutagen`, `MP3`, `num_frames`, `frame_rate`, `16fps`

## Phụ thuộc
- Import: `core.config.settings`
- Import bởi: `services/storyboard_orchestrator.py`, `routers/storyboard_router.py`
- Test: `test/test_audio_service.py`
