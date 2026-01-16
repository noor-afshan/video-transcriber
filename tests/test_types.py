"""Tests for modules/types.py - DiarizedSegment dataclass."""

import pytest

from modules.types import DiarizedSegment


class TestDiarizedSegment:
    """Tests for DiarizedSegment dataclass."""

    def test_creation_with_all_fields(self):
        """Test creating a segment with all fields."""
        seg = DiarizedSegment(
            start=10.5,
            end=15.3,
            text="Hello world",
            speaker="Speaker 1",
        )

        assert seg.start == 10.5
        assert seg.end == 15.3
        assert seg.text == "Hello world"
        assert seg.speaker == "Speaker 1"

    def test_default_speaker(self):
        """Test that speaker defaults to 'Unknown'."""
        seg = DiarizedSegment(start=0.0, end=5.0, text="Test")

        assert seg.speaker == "Unknown"

    def test_duration_property(self):
        """Test the duration computed property."""
        seg = DiarizedSegment(start=10.0, end=25.0, text="Test")

        assert seg.duration == 15.0

    def test_duration_with_fractional_seconds(self):
        """Test duration with fractional seconds."""
        seg = DiarizedSegment(start=1.5, end=3.7, text="Test")

        assert seg.duration == pytest.approx(2.2, rel=1e-9)

    def test_midpoint_property(self):
        """Test the midpoint computed property."""
        seg = DiarizedSegment(start=10.0, end=20.0, text="Test")

        assert seg.midpoint == 15.0

    def test_midpoint_with_odd_duration(self):
        """Test midpoint with non-integer midpoint."""
        seg = DiarizedSegment(start=0.0, end=5.0, text="Test")

        assert seg.midpoint == 2.5

    def test_to_tuple_format(self):
        """Test conversion to legacy tuple format."""
        seg = DiarizedSegment(
            start=1.0,
            end=5.0,
            text="Hello",
            speaker="Speaker 2",
        )

        result = seg.to_tuple()

        assert result == ("Speaker 2", 1.0, 5.0, "Hello")
        assert isinstance(result, tuple)
        assert len(result) == 4

    def test_from_tuple_creation(self):
        """Test creating segment from legacy tuple."""
        legacy_tuple = ("Speaker 1", 2.5, 7.5, "Test text")

        seg = DiarizedSegment.from_tuple(legacy_tuple)

        assert seg.start == 2.5
        assert seg.end == 7.5
        assert seg.text == "Test text"
        assert seg.speaker == "Speaker 1"

    def test_roundtrip_tuple_conversion(self):
        """Test that to_tuple -> from_tuple preserves data."""
        original = DiarizedSegment(
            start=3.14,
            end=6.28,
            text="Pi segment",
            speaker="Mathematician",
        )

        roundtrip = DiarizedSegment.from_tuple(original.to_tuple())

        assert roundtrip.start == original.start
        assert roundtrip.end == original.end
        assert roundtrip.text == original.text
        assert roundtrip.speaker == original.speaker

    def test_equality(self):
        """Test that equal segments compare equal."""
        seg1 = DiarizedSegment(start=0.0, end=5.0, text="Same", speaker="Speaker 1")
        seg2 = DiarizedSegment(start=0.0, end=5.0, text="Same", speaker="Speaker 1")

        assert seg1 == seg2

    def test_inequality_different_text(self):
        """Test that segments with different text are not equal."""
        seg1 = DiarizedSegment(start=0.0, end=5.0, text="Text A", speaker="Speaker 1")
        seg2 = DiarizedSegment(start=0.0, end=5.0, text="Text B", speaker="Speaker 1")

        assert seg1 != seg2

    def test_str_representation(self):
        """Test string representation includes key fields."""
        seg = DiarizedSegment(start=0.0, end=5.0, text="Hello", speaker="Speaker 1")

        str_repr = str(seg)

        assert "0.0" in str_repr
        assert "5.0" in str_repr
        assert "Hello" in str_repr
        assert "Speaker 1" in str_repr

    def test_zero_duration_segment(self):
        """Test segment with zero duration."""
        seg = DiarizedSegment(start=5.0, end=5.0, text="Instant")

        assert seg.duration == 0.0
        assert seg.midpoint == 5.0

    def test_empty_text(self):
        """Test segment with empty text."""
        seg = DiarizedSegment(start=0.0, end=1.0, text="", speaker="Speaker 1")

        assert seg.text == ""
        assert seg.duration == 1.0
