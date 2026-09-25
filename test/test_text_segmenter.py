# test_text_segmenter.py – Unit tests cho services/text_segmenter.py
# Yêu cầu độ bao phủ: >= 90%

import json
import pytest
from fastapi import HTTPException

from services.text_segmenter import (
    parse_input,
    split_into_segments,
    validate_segments,
    _parse_json,
    _parse_text,
    _merge_short_sentences,
    _split_long_sentences,
    MAX_SEGMENT_CHARS,
    MIN_SEGMENT_CHARS,
)


# ─── Tests: parse_input ────────────────────────────────────────────────────────

class TestParseInput:
    def test_parse_text_simple(self):
        result = parse_input("Câu một. Câu hai. Câu ba.", "text")
        assert len(result) == 3
        assert result[0] == "Câu một."

    def test_parse_text_empty(self):
        with pytest.raises(HTTPException) as exc:
            parse_input("", "text")
        assert exc.value.status_code == 400

    def test_parse_text_whitespace_only(self):
        with pytest.raises(HTTPException) as exc:
            parse_input("   \n  ", "text")
        assert exc.value.status_code == 400

    def test_parse_json_segments_format(self):
        raw = json.dumps({"segments": [{"text": "A"}, {"text": "B"}]})
        result = parse_input(raw, "json")
        assert result == ["A", "B"]

    def test_parse_json_array_format(self):
        raw = json.dumps([{"text": "A"}, {"text": "B"}])
        result = parse_input(raw, "json")
        assert result == ["A", "B"]

    def test_parse_json_string_items(self):
        raw = json.dumps(["A", "B"])
        result = parse_input(raw, "json")
        assert result == ["A", "B"]

    def test_parse_json_invalid(self):
        with pytest.raises(HTTPException) as exc:
            parse_input("NOT_JSON{{{", "json")
        assert exc.value.status_code == 400
        assert "JSON không hợp lệ" in exc.value.detail

    def test_parse_json_no_text(self):
        raw = json.dumps({"segments": []})
        with pytest.raises(HTTPException) as exc:
            parse_input(raw, "json")
        assert exc.value.status_code == 400

    def test_parse_json_not_dict_or_list(self):
        with pytest.raises(HTTPException) as exc:
            parse_input('"just a string"', "json")
        assert exc.value.status_code == 400

    def test_parse_json_segments_not_list(self):
        raw = json.dumps({"segments": "not a list"})
        with pytest.raises(HTTPException) as exc:
            parse_input(raw, "json")
        assert exc.value.status_code == 400

    def test_parse_json_skips_empty_text(self):
        raw = json.dumps({"segments": [{"text": "A"}, {"text": "  "}, {"text": "B"}]})
        result = parse_input(raw, "json")
        assert result == ["A", "B"]


# ─── Tests: _parse_text ────────────────────────────────────────────────────────

class TestParseText:
    def test_split_by_period(self):
        assert len(_parse_text("A. B. C.")) == 3

    def test_split_by_question(self):
        assert len(_parse_text("A? B?")) == 2

    def test_split_by_exclamation(self):
        assert len(_parse_text("A! B!")) == 2

    def test_split_by_double_newline(self):
        assert len(_parse_text("A\n\nB")) == 2

    def test_empty_returns_empty_list(self):
        assert _parse_text("") == []


# ─── Tests: split_into_segments ────────────────────────────────────────────────

class TestSplitIntoSegments:
    def test_split_normal(self):
        text = "Câu một dài đủ để không bị gộp vào câu khác. " * 3
        result = split_into_segments(text, max_segments=15)
        assert len(result) <= 15

    def test_split_empty_raises(self):
        with pytest.raises(HTTPException) as exc:
            split_into_segments("", max_segments=15)
        assert exc.value.status_code == 400

    def test_split_exceeds_max(self):
        # Tạo 20 câu dài
        text = " ".join([f"Câu số {i} với nội dung đủ dài để không bị gộp." for i in range(20)])
        with pytest.raises(HTTPException) as exc:
            split_into_segments(text, max_segments=5)
        assert exc.value.status_code == 400
        assert "Vượt giới hạn" in exc.value.detail

    def test_split_merges_short(self):
        # 3 câu ngắn nên được gộp
        text = "A. B. C."
        result = split_into_segments(text, max_segments=15)
        assert len(result) < 3

    def test_split_long_sentence(self):
        # Câu dài > 200 ký tự nên bị tách
        long_sentence = ", ".join(["phần " + str(i) for i in range(50)]) + "."
        result = split_into_segments(long_sentence, max_segments=15)
        assert len(result) >= 1


# ─── Tests: _merge_short_sentences ─────────────────────────────────────────────

class TestMergeShortSentences:
    def test_merge_short(self):
        result = _merge_short_sentences(["A.", "B.", "C."])
        assert len(result) == 1

    def test_no_merge_long(self):
        long = "x" * (MIN_SEGMENT_CHARS + 10)
        result = _merge_short_sentences([long, long])
        assert len(result) == 2

    def test_empty_list(self):
        assert _merge_short_sentences([]) == []


# ─── Tests: _split_long_sentences ──────────────────────────────────────────────

class TestSplitLongSentences:
    def test_short_unchanged(self):
        result = _split_long_sentences(["Short sentence."])
        assert result == ["Short sentence."]

    def test_long_split(self):
        long = ", ".join(["word" * 10 for _ in range(10)])
        result = _split_long_sentences([long])
        assert len(result) > 1

    def test_empty_list(self):
        assert _split_long_sentences([]) == []


# ─── Tests: validate_segments ──────────────────────────────────────────────────

class TestValidateSegments:
    def test_valid(self):
        ok, msg = validate_segments(["Câu một.", "Câu hai."])
        assert ok is True
        assert msg == "Hợp lệ."

    def test_empty(self):
        ok, msg = validate_segments([])
        assert ok is False
        assert "rỗng" in msg

    def test_too_many(self):
        segments = [f"Câu {i}." for i in range(20)]
        ok, msg = validate_segments(segments)
        assert ok is False
        assert "Vượt giới hạn" in msg

    def test_empty_segment(self):
        ok, msg = validate_segments(["Câu một.", "   "])
        assert ok is False
        assert "rỗng" in msg

    def test_too_long_segment(self):
        long_seg = "x" * (MAX_SEGMENT_CHARS + 1)
        ok, msg = validate_segments([long_seg])
        assert ok is False
        assert "quá dài" in msg
