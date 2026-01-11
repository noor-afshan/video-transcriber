"""Transcript cleanup module for removing hallucinations and repetitions."""

import re
from difflib import SequenceMatcher


class TranscriptCleaner:
    """Post-processing to clean up Whisper transcription artifacts."""

    # Filler words and short meaningless segments (case-insensitive)
    FILLER_PATTERNS = [
        r"^(uh+|um+|hmm+|huh|mhm|ah+)\.?$",
        r"^(yeah|yep|yes|okay|ok|right|sure)\.?$",
        r"^[.,!?;:\-]+$",  # punctuation only
        r"^\s*$",  # whitespace only
    ]

    # Known Whisper hallucination patterns
    HALLUCINATION_PATTERNS = [
        r"thanks for watching",
        r"thank you for watching",
        r"subscribe.*channel",
        r"please like.*comment",
        r"don't forget to subscribe",
        r"see you in the next",
        r"\[music\]",
        r"\[applause\]",
        r"\(music\)",
        r"\(applause\)",
    ]

    # Non-English character ranges (Chinese, Japanese, Korean)
    NON_ENGLISH_PATTERN = re.compile(r"[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]")

    def __init__(
        self,
        remove_duplicates: bool = True,
        remove_fillers: bool = True,
        remove_hallucinations: bool = True,
        remove_non_english: bool = True,
        min_segment_length: int = 3,
        similarity_threshold: float = 0.9,
    ):
        """
        Initialize the cleaner.

        Args:
            remove_duplicates: Remove consecutive duplicate lines
            remove_fillers: Remove short filler words (yeah, uh, etc.)
            remove_hallucinations: Remove known Whisper hallucination patterns
            remove_non_english: Remove segments with non-English characters
            min_segment_length: Minimum character length for segments
            similarity_threshold: Threshold for duplicate detection (0.0-1.0)
        """
        self.remove_duplicates = remove_duplicates
        self.remove_fillers = remove_fillers
        self.remove_hallucinations = remove_hallucinations
        self.remove_non_english = remove_non_english
        self.min_segment_length = min_segment_length
        self.similarity_threshold = similarity_threshold

        # Compile patterns
        self._filler_regex = [re.compile(p, re.IGNORECASE) for p in self.FILLER_PATTERNS]
        self._hallucination_regex = [re.compile(p, re.IGNORECASE) for p in self.HALLUCINATION_PATTERNS]

    def clean(self, segments: list) -> list:
        """
        Clean a list of transcript segments.

        Args:
            segments: List of (speaker, start, end, text) tuples or TranscriptSegment objects

        Returns:
            Cleaned list with artifacts removed
        """
        if not segments:
            return segments

        cleaned = segments.copy()

        if self.remove_non_english:
            cleaned = self._filter_non_english(cleaned)

        if self.remove_hallucinations:
            cleaned = self._filter_hallucinations(cleaned)

        if self.remove_fillers:
            cleaned = self._filter_fillers(cleaned)

        if self.remove_duplicates:
            cleaned = self._filter_duplicates(cleaned)

        # Filter by minimum length
        cleaned = self._filter_short(cleaned)

        return cleaned

    def _get_text(self, segment) -> str:
        """Extract text from segment (handles both tuples and objects)."""
        if hasattr(segment, "text"):
            return segment.text
        elif isinstance(segment, tuple) and len(segment) >= 4:
            return segment[3]  # (speaker, start, end, text)
        return str(segment)

    def _filter_non_english(self, segments: list) -> list:
        """Remove segments containing non-English characters."""
        result = []
        for seg in segments:
            text = self._get_text(seg)
            if not self.NON_ENGLISH_PATTERN.search(text):
                result.append(seg)
        return result

    def _filter_hallucinations(self, segments: list) -> list:
        """Remove segments matching known hallucination patterns."""
        result = []
        for seg in segments:
            text = self._get_text(seg).lower()
            is_hallucination = any(pattern.search(text) for pattern in self._hallucination_regex)
            if not is_hallucination:
                result.append(seg)
        return result

    def _filter_fillers(self, segments: list) -> list:
        """Remove short filler word segments."""
        result = []
        for seg in segments:
            text = self._get_text(seg).strip()
            is_filler = any(pattern.match(text) for pattern in self._filler_regex)
            if not is_filler:
                result.append(seg)
        return result

    def _filter_duplicates(self, segments: list) -> list:
        """Remove consecutive duplicate or near-duplicate lines."""
        if len(segments) < 2:
            return segments

        result = [segments[0]]
        prev_text = self._get_text(segments[0]).strip().lower()

        for seg in segments[1:]:
            curr_text = self._get_text(seg).strip().lower()

            # Check similarity
            similarity = SequenceMatcher(None, prev_text, curr_text).ratio()

            if similarity < self.similarity_threshold:
                result.append(seg)
                prev_text = curr_text
            # else: skip duplicate

        return result

    def _filter_short(self, segments: list) -> list:
        """Remove segments shorter than minimum length."""
        result = []
        for seg in segments:
            text = self._get_text(seg).strip()
            if len(text) >= self.min_segment_length:
                result.append(seg)
        return result

    def clean_text(self, text: str) -> str:
        """Clean a single text string (for simple use cases)."""
        # Remove non-English
        if self.remove_non_english and self.NON_ENGLISH_PATTERN.search(text):
            return ""

        # Check hallucinations
        if self.remove_hallucinations:
            lower = text.lower()
            if any(pattern.search(lower) for pattern in self._hallucination_regex):
                return ""

        # Check fillers
        if self.remove_fillers:
            stripped = text.strip()
            if any(pattern.match(stripped) for pattern in self._filler_regex):
                return ""

        # Check length
        if len(text.strip()) < self.min_segment_length:
            return ""

        return text
