"""Shared data types for the transcription pipeline."""

from dataclasses import dataclass


@dataclass
class DiarizedSegment:
    """
    A transcript segment with speaker attribution.

    This is the unified type used after merging transcription with speaker
    diarization, and throughout the rest of the pipeline (cleaning, output).

    Attributes:
        start: Start time in seconds
        end: End time in seconds
        text: Transcribed text content
        speaker: Speaker label (e.g., "Speaker 1", "Unknown")
    """
    start: float
    end: float
    text: str
    speaker: str = "Unknown"

    @property
    def duration(self) -> float:
        """Duration of the segment in seconds."""
        return self.end - self.start

    @property
    def midpoint(self) -> float:
        """Midpoint timestamp, useful for speaker assignment."""
        return (self.start + self.end) / 2

    def to_tuple(self) -> tuple[str, float, float, str]:
        """Convert to legacy tuple format (speaker, start, end, text)."""
        return (self.speaker, self.start, self.end, self.text)

    @classmethod
    def from_tuple(cls, t: tuple[str, float, float, str]) -> "DiarizedSegment":
        """Create from legacy tuple format (speaker, start, end, text)."""
        speaker, start, end, text = t
        return cls(start=start, end=end, text=text, speaker=speaker)
