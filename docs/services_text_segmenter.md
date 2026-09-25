# services/text_segmenter.py

## Mục đích
Parse input (text/JSON) và chia thành các segment có nghĩa, giới hạn 15 segment.

## Functions
### `parse_input(raw_text, input_format) -> List[str]`
- **Input**: text thuần hoặc JSON string
- **Output**: danh sách text segments
- **Lỗi**: 400 nếu rỗng hoặc JSON hỏng

### `split_into_segments(text, max_segments=15) -> List[str]`
- Gộp câu ngắn, tách câu dài
- **Lỗi**: 400 nếu vượt 15 segment

### `validate_segments(segments) -> Tuple[bool, str]`
- Kiểm tra rỗng, số lượng, độ dài

## Hằng số
| Hằng | Giá trị |
|---|---|
| `MAX_SEGMENT_CHARS` | 200 |
| `MIN_SEGMENT_CHARS` | 50 |

## Keywords
`text_segmenter`, `parse_input`, `split_into_segments`, `validate_segments`, `MAX_SEGMENT_CHARS`, `segment`, `JSON parse`, `text split`

## Phụ thuộc
- Import: `core.config.settings`
- Import bởi: `services/storyboard_orchestrator.py`
- Test: `test/test_text_segmenter.py`
