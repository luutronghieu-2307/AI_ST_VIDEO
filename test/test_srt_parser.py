import pytest
from fastapi import HTTPException
from services.srt_parser import (
    parse_timestamp,
    calculate_frames_1_plus_8k,
    parse_srt,
    ParsedSrtSegment,
)

SAMPLE_SRT = """1
00:00:00,100 --> 00:00:04,292
Trí tuệ nhân tạo hay AI không phải là một thực thể có ý thức

2
00:00:04,850 --> 00:00:08,383
Bản chất của AI thực chất là những thuật toán phức tạp

3
00:00:08,533 --> 00:00:09,883
dự đoán và tự động hóa các tác vụ
"""


class TestParseTimestamp:
    def test_parse_valid_comma(self):
        assert parse_timestamp("00:00:04,292") == 4.292
        assert parse_timestamp("01:02:03,500") == 3723.5

    def test_parse_valid_dot(self):
        assert parse_timestamp("00:00:04.292") == 4.292

    def test_parse_zero(self):
        assert parse_timestamp("00:00:00,000") == 0.0

    def test_parse_invalid_format(self):
        with pytest.raises(ValueError):
            parse_timestamp("04:292")


class TestCalculateFrames:
    def test_calculate_standard_durations(self):
        # 4.192s @ 16fps = 67.07 -> 65 frames (1 + 8*8)
        assert calculate_frames_1_plus_8k(4.192, fps=16) == 65
        # 3.533s @ 16fps = 56.52 -> 57 frames (1 + 8*7)
        assert calculate_frames_1_plus_8k(3.533, fps=16) == 57
        # 1.35s @ 16fps = 21.6 -> min clamp 25 frames
        assert calculate_frames_1_plus_8k(1.35, fps=16) == 25

    def test_calculate_min_clamp(self):
        assert calculate_frames_1_plus_8k(0.5, fps=16) == 25

    def test_calculate_max_clamp(self):
        assert calculate_frames_1_plus_8k(20.0, fps=16) == 121


class TestParseSrt:
    def test_parse_sample_srt_success(self):
        segments = parse_srt(SAMPLE_SRT, fps=16)
        assert len(segments) == 3
        
        # Segment 1
        seg1 = segments[0]
        assert seg1.order == 1
        assert seg1.start_sec == 0.1
        assert seg1.end_sec == 4.292
        assert seg1.duration_sec == 4.192
        assert seg1.num_frames == 65
        assert "Trí tuệ nhân tạo" in seg1.text

        # Segment 2
        seg2 = segments[1]
        assert seg2.order == 2
        assert seg2.start_sec == 4.85
        assert seg2.end_sec == 8.383
        assert seg2.num_frames == 57

        # Segment 3 (segment cuối cùng được cộng thêm +1.0s padding)
        seg3 = segments[2]
        assert seg3.order == 3
        assert seg3.start_sec == 8.533
        assert seg3.end_sec == round(9.883 + 1.0, 3)
        assert seg3.duration_sec == round(1.35 + 1.0, 3)
        # 2.35s @ 16fps = 37.6 -> 41 frames (1+8*5)
        assert seg3.num_frames == 41

    def test_parse_empty_content_raises(self):

        with pytest.raises(HTTPException) as exc:
            parse_srt("")
        assert exc.value.status_code == 400

    def test_parse_invalid_structure_raises(self):
        with pytest.raises(HTTPException) as exc:
            parse_srt("Đây là một đoạn text không có timecode")
        assert exc.value.status_code == 400

    def test_parse_inverted_timestamp_raises(self):
        bad_srt = "1\n00:00:05,000 --> 00:00:02,000\nLỗi thời gian đảo ngược"
        with pytest.raises(HTTPException) as exc:
            parse_srt(bad_srt)
        assert exc.value.status_code == 400
        assert "phải lớn hơn thời gian bắt đầu" in exc.value.detail

    def test_parse_exceed_max_segments(self):
        many_segs = "\n\n".join(
            f"{i}\n00:00:{i:02d},000 --> 00:00:{i+1:02d},000\nĐoạn {i}"
            for i in range(5)
        )
        with pytest.raises(HTTPException) as exc:
            parse_srt(many_segs, max_segments=3)
        assert exc.value.status_code == 400
        assert "vượt quá giới hạn" in exc.value.detail
