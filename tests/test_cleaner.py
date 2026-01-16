"""Tests for modules/cleaner.py - TranscriptCleaner."""

import pytest

from modules.cleaner import TranscriptCleaner
from modules.types import DiarizedSegment


class TestTranscriptCleanerInit:
    """Tests for TranscriptCleaner initialization."""

    def test_default_settings(self):
        """Test default cleaner settings."""
        cleaner = TranscriptCleaner()

        assert cleaner.remove_duplicates is True
        assert cleaner.remove_fillers is True
        assert cleaner.remove_hallucinations is True
        assert cleaner.remove_non_english is True
        assert cleaner.min_segment_length == 3
        assert cleaner.similarity_threshold == 0.9

    def test_custom_settings(self):
        """Test custom cleaner settings."""
        cleaner = TranscriptCleaner(
            remove_duplicates=False,
            remove_fillers=False,
            min_segment_length=10,
            similarity_threshold=0.8,
        )

        assert cleaner.remove_duplicates is False
        assert cleaner.remove_fillers is False
        assert cleaner.min_segment_length == 10
        assert cleaner.similarity_threshold == 0.8


class TestHallucinationRemoval:
    """Tests for hallucination pattern removal."""

    @pytest.fixture
    def cleaner(self):
        """Cleaner configured for hallucination removal only."""
        return TranscriptCleaner(
            remove_hallucinations=True,
            remove_duplicates=False,
            remove_fillers=False,
            remove_non_english=False,
            min_segment_length=0,
        )

    def test_removes_thanks_for_watching(self, cleaner):
        """Test removal of 'thanks for watching' pattern."""
        segments = [
            DiarizedSegment(0, 5, "Real content here.", "Speaker 1"),
            DiarizedSegment(5, 10, "Thanks for watching!", "Speaker 1"),
        ]

        result = cleaner.clean(segments)

        assert len(result) == 1
        assert result[0].text == "Real content here."

    def test_removes_subscribe_pattern(self, cleaner):
        """Test removal of subscribe pattern."""
        segments = [
            DiarizedSegment(0, 5, "Real content.", "Speaker 1"),
            DiarizedSegment(5, 10, "Please subscribe to my channel!", "Speaker 1"),
        ]

        result = cleaner.clean(segments)

        assert len(result) == 1

    def test_removes_music_markers(self, cleaner):
        """Test removal of [music] markers."""
        segments = [
            DiarizedSegment(0, 5, "[music]", "Unknown"),
            DiarizedSegment(5, 10, "Hello everyone.", "Speaker 1"),
            DiarizedSegment(10, 15, "(music)", "Unknown"),
        ]

        result = cleaner.clean(segments)

        assert len(result) == 1
        assert result[0].text == "Hello everyone."

    def test_case_insensitive(self, cleaner):
        """Test that patterns are case-insensitive."""
        segments = [
            DiarizedSegment(0, 5, "THANKS FOR WATCHING", "Speaker 1"),
            DiarizedSegment(5, 10, "ThAnKs FoR wAtChInG", "Speaker 1"),
        ]

        result = cleaner.clean(segments)

        assert len(result) == 0

    def test_preserves_non_hallucinations(self, cleaner, sample_diarized_segments):
        """Test that normal content is preserved."""
        result = cleaner.clean(sample_diarized_segments)

        assert len(result) == len(sample_diarized_segments)


class TestDuplicateRemoval:
    """Tests for duplicate/near-duplicate removal."""

    @pytest.fixture
    def cleaner(self):
        """Cleaner configured for duplicate removal only."""
        return TranscriptCleaner(
            remove_duplicates=True,
            remove_hallucinations=False,
            remove_fillers=False,
            remove_non_english=False,
            min_segment_length=0,
            similarity_threshold=0.9,
        )

    def test_removes_exact_duplicates(self, cleaner):
        """Test removal of exact consecutive duplicates."""
        segments = [
            DiarizedSegment(0, 5, "Hello there.", "Speaker 1"),
            DiarizedSegment(5, 10, "Hello there.", "Speaker 1"),
            DiarizedSegment(10, 15, "Something different.", "Speaker 1"),
        ]

        result = cleaner.clean(segments)

        assert len(result) == 2
        assert result[0].text == "Hello there."
        assert result[1].text == "Something different."

    def test_removes_near_duplicates(self, cleaner):
        """Test removal of near-duplicate segments."""
        segments = [
            DiarizedSegment(0, 5, "Hello there everyone.", "Speaker 1"),
            DiarizedSegment(5, 10, "Hello there everyone!", "Speaker 1"),  # Very similar
        ]

        result = cleaner.clean(segments)

        assert len(result) == 1

    def test_keeps_different_segments(self, cleaner):
        """Test that sufficiently different segments are kept."""
        segments = [
            DiarizedSegment(0, 5, "This is about cats.", "Speaker 1"),
            DiarizedSegment(5, 10, "Now let's talk about dogs.", "Speaker 1"),
        ]

        result = cleaner.clean(segments)

        assert len(result) == 2

    def test_non_consecutive_duplicates_kept(self, cleaner):
        """Test that non-consecutive duplicates are not removed."""
        segments = [
            DiarizedSegment(0, 5, "Hello.", "Speaker 1"),
            DiarizedSegment(5, 10, "Something else.", "Speaker 1"),
            DiarizedSegment(10, 15, "Hello.", "Speaker 1"),  # Same as first, but not consecutive
        ]

        result = cleaner.clean(segments)

        assert len(result) == 3

    def test_custom_similarity_threshold(self):
        """Test custom similarity threshold."""
        # Low threshold - more aggressive removal
        cleaner = TranscriptCleaner(
            remove_duplicates=True,
            similarity_threshold=0.5,
            remove_hallucinations=False,
            remove_fillers=False,
            remove_non_english=False,
            min_segment_length=0,
        )

        segments = [
            DiarizedSegment(0, 5, "Hello there.", "Speaker 1"),
            DiarizedSegment(5, 10, "Hello here.", "Speaker 1"),  # 50% similar
        ]

        result = cleaner.clean(segments)

        assert len(result) == 1


class TestFillerRemoval:
    """Tests for filler word removal."""

    @pytest.fixture
    def cleaner(self):
        """Cleaner configured for filler removal only."""
        return TranscriptCleaner(
            remove_fillers=True,
            remove_duplicates=False,
            remove_hallucinations=False,
            remove_non_english=False,
            min_segment_length=0,
        )

    def test_removes_um(self, cleaner):
        """Test removal of 'um' filler."""
        segments = [
            DiarizedSegment(0, 2, "Um", "Speaker 1"),
            DiarizedSegment(2, 7, "I was thinking about it.", "Speaker 1"),
        ]

        result = cleaner.clean(segments)

        assert len(result) == 1
        assert result[0].text == "I was thinking about it."

    def test_removes_uh(self, cleaner):
        """Test removal of 'uh' filler."""
        segments = [
            DiarizedSegment(0, 2, "Uh", "Speaker 1"),
            DiarizedSegment(2, 7, "Let me think.", "Speaker 1"),
        ]

        result = cleaner.clean(segments)

        assert len(result) == 1

    def test_removes_yeah_standalone(self, cleaner):
        """Test removal of standalone 'yeah'."""
        segments = [
            DiarizedSegment(0, 2, "Yeah", "Speaker 1"),
            DiarizedSegment(2, 7, "That makes sense.", "Speaker 1"),
        ]

        result = cleaner.clean(segments)

        assert len(result) == 1

    def test_keeps_yeah_in_sentence(self, cleaner):
        """Test that 'yeah' in a sentence is kept."""
        segments = [
            DiarizedSegment(0, 5, "Yeah, I agree with that point.", "Speaker 1"),
        ]

        result = cleaner.clean(segments)

        assert len(result) == 1

    def test_removes_punctuation_only(self, cleaner):
        """Test removal of punctuation-only segments."""
        segments = [
            DiarizedSegment(0, 1, "...", "Speaker 1"),
            DiarizedSegment(1, 5, "Real content.", "Speaker 1"),
            DiarizedSegment(5, 6, "?!", "Speaker 1"),
        ]

        result = cleaner.clean(segments)

        assert len(result) == 1
        assert result[0].text == "Real content."


class TestNonEnglishRemoval:
    """Tests for non-English character removal."""

    @pytest.fixture
    def cleaner(self):
        """Cleaner configured for non-English removal only."""
        return TranscriptCleaner(
            remove_non_english=True,
            remove_duplicates=False,
            remove_hallucinations=False,
            remove_fillers=False,
            min_segment_length=0,
        )

    def test_removes_chinese(self, cleaner):
        """Test removal of Chinese characters."""
        segments = [
            DiarizedSegment(0, 5, "Hello world.", "Speaker 1"),
            DiarizedSegment(5, 10, "你好世界", "Speaker 1"),
        ]

        result = cleaner.clean(segments)

        assert len(result) == 1
        assert result[0].text == "Hello world."

    def test_removes_japanese(self, cleaner):
        """Test removal of Japanese characters."""
        segments = [
            DiarizedSegment(0, 5, "こんにちは", "Speaker 1"),
            DiarizedSegment(5, 10, "Good morning.", "Speaker 1"),
        ]

        result = cleaner.clean(segments)

        assert len(result) == 1
        assert result[0].text == "Good morning."

    def test_removes_korean(self, cleaner):
        """Test removal of Korean characters."""
        segments = [
            DiarizedSegment(0, 5, "안녕하세요", "Speaker 1"),
        ]

        result = cleaner.clean(segments)

        assert len(result) == 0

    def test_keeps_english_with_numbers(self, cleaner):
        """Test that English with numbers is kept."""
        segments = [
            DiarizedSegment(0, 5, "The meeting is at 3:30 PM.", "Speaker 1"),
        ]

        result = cleaner.clean(segments)

        assert len(result) == 1


class TestMinSegmentLength:
    """Tests for minimum segment length filtering."""

    def test_removes_short_segments(self):
        """Test removal of segments below minimum length."""
        cleaner = TranscriptCleaner(
            min_segment_length=10,
            remove_duplicates=False,
            remove_hallucinations=False,
            remove_fillers=False,
            remove_non_english=False,
        )

        segments = [
            DiarizedSegment(0, 2, "Hi", "Speaker 1"),  # 2 chars
            DiarizedSegment(2, 7, "This is a longer segment.", "Speaker 1"),  # 25 chars
        ]

        result = cleaner.clean(segments)

        assert len(result) == 1
        assert result[0].text == "This is a longer segment."

    def test_default_min_length(self):
        """Test default minimum length of 3."""
        cleaner = TranscriptCleaner(
            remove_duplicates=False,
            remove_hallucinations=False,
            remove_fillers=False,
            remove_non_english=False,
        )

        segments = [
            DiarizedSegment(0, 1, "Hi", "Speaker 1"),  # 2 chars - removed
            DiarizedSegment(1, 2, "Hey", "Speaker 1"),  # 3 chars - kept
        ]

        result = cleaner.clean(segments)

        assert len(result) == 1
        assert result[0].text == "Hey"


class TestCleanEmpty:
    """Tests for edge cases with empty input."""

    def test_empty_list(self):
        """Test cleaning empty list."""
        cleaner = TranscriptCleaner()

        result = cleaner.clean([])

        assert result == []

    def test_single_segment(self):
        """Test cleaning single valid segment."""
        cleaner = TranscriptCleaner()

        segments = [
            DiarizedSegment(0, 5, "Single valid segment here.", "Speaker 1"),
        ]

        result = cleaner.clean(segments)

        assert len(result) == 1


class TestCleanText:
    """Tests for clean_text method."""

    def test_clean_valid_text(self):
        """Test cleaning valid text string."""
        cleaner = TranscriptCleaner()

        result = cleaner.clean_text("This is valid text.")

        assert result == "This is valid text."

    def test_clean_hallucination_text(self):
        """Test cleaning hallucination text."""
        cleaner = TranscriptCleaner()

        result = cleaner.clean_text("Thanks for watching!")

        assert result == ""

    def test_clean_short_text(self):
        """Test cleaning short text."""
        cleaner = TranscriptCleaner(min_segment_length=10)

        result = cleaner.clean_text("Hi")

        assert result == ""
