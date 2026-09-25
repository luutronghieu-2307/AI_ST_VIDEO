# services/video_prompt_service.py

## Mục đích
Gọi GPT-120B sinh prompt video cho LTX 2.5 từ segment text.

## Functions
### `build_video_prompt(segment_text, context, style) -> str`
- Gọi `groq_service._call_chat_completions()`
- Model: `settings.GROQ_CREATIVE_MODEL` (openai/gpt-oss-120b)
- Output: prompt tiếng Anh, documentary style

### `build_batch_video_prompts(segments, context) -> List[str]`
- Xử lý tuần tự, không dừng khi 1 segment lỗi

## Hằng số
| Hằng | Giá trị |
|---|---|
| `SYSTEM_PROMPT_VIDEO` | Prompt hệ thống (documentary style) |
| `DEFAULT_NEGATIVE_PROMPT` | `blurry, low quality, distorted...` |

## Keywords
`video_prompt_service`, `build_video_prompt`, `build_batch_video_prompts`, `SYSTEM_PROMPT_VIDEO`, `DEFAULT_NEGATIVE_PROMPT`, `GPT-120B`, `gpt-oss-120b`, `documentary`, `prompt engineering`

## Phụ thuộc
- Import: `core.config.settings`, `services.groq_service`
- Import bởi: `services/storyboard_orchestrator.py`
- Test: `test/test_video_prompt_service.py`
