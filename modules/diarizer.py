"""Speaker diarization module using pyannote-audio."""

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SpeakerSegment:
    """A speaker segment with timing."""
    start: float
    end: float
    speaker: str


class Diarizer:
    """Speaker diarization using pyannote-audio."""

    def __init__(self, hf_token: str = None, min_speakers: int = 2, max_speakers: int = 6):
        """
        Initialize the diarizer.

        Args:
            hf_token: HuggingFace token for pyannote models. Falls back to HF_TOKEN env var.
            min_speakers: Minimum expected speakers
            max_speakers: Maximum expected speakers
        """
        self.hf_token = hf_token or os.environ.get("HF_TOKEN")
        self.min_speakers = min_speakers
        self.max_speakers = max_speakers
        self._pipeline = None

        if not self.hf_token:
            raise ValueError(
                "HuggingFace token required for pyannote models.\n"
                "1. Get a token at https://huggingface.co/settings/tokens\n"
                "2. Accept model terms at https://huggingface.co/pyannote/speaker-diarization-3.1\n"
                "3. Set HF_TOKEN environment variable or pass hf_token parameter"
            )

    def __repr__(self) -> str:
        """Safe representation that doesn't expose the token."""
        return f"Diarizer(hf_token='***', min_speakers={self.min_speakers}, max_speakers={self.max_speakers})"

    def _load_pipeline(self):
        """Lazy-load the pyannote pipeline."""
        if self._pipeline is None:
            try:
                from pyannote.audio import Pipeline
            except ImportError:
                raise ImportError("pyannote.audio not installed. Run: pip install pyannote.audio")

            print("Loading speaker diarization model...")
            self._pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                token=self.hf_token  # 'use_auth_token' is deprecated
            )
        return self._pipeline

    def diarize(self, audio_path: str | Path) -> list[SpeakerSegment]:
        """
        Identify speakers in an audio file.

        Args:
            audio_path: Path to audio/video file

        Returns:
            List of SpeakerSegment with speaker labels (Speaker 1, Speaker 2, etc.)
        """
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"File not found: {audio_path}")

        pipeline = self._load_pipeline()

        print(f"Identifying speakers in: {audio_path.name}")
        print("This may take a while...\n")

        diarization = pipeline(
            str(audio_path),
            min_speakers=self.min_speakers,
            max_speakers=self.max_speakers
        )

        segments = []
        speaker_map = {}  # Map SPEAKER_00 -> "Speaker 1"
        speaker_count = 0

        for turn, _, speaker in diarization.itertracks(yield_label=True):
            if speaker not in speaker_map:
                speaker_count += 1
                speaker_map[speaker] = f"Speaker {speaker_count}"

            segments.append(SpeakerSegment(
                start=turn.start,
                end=turn.end,
                speaker=speaker_map[speaker]
            ))

        print(f"Identified {len(speaker_map)} speakers\n")
        return segments


def get_speaker_at_time(segments: list[SpeakerSegment], timestamp: float) -> str:
    """
    Find which speaker is talking at a given timestamp.

    Args:
        segments: List of speaker segments
        timestamp: Time in seconds

    Returns:
        Speaker label or "Unknown" if no match
    """
    for seg in segments:
        if seg.start <= timestamp <= seg.end:
            return seg.speaker
    return "Unknown"


def assign_speakers_to_transcript(
    transcript_segments: list,
    speaker_segments: list[SpeakerSegment]
) -> list[tuple]:
    """
    Merge transcript segments with speaker labels.

    Uses the midpoint of each transcript segment to find the speaker.

    Args:
        transcript_segments: List of TranscriptSegment from transcriber
        speaker_segments: List of SpeakerSegment from diarizer

    Returns:
        List of (speaker, start, end, text) tuples
    """
    results = []

    for ts in transcript_segments:
        # Use midpoint for matching
        midpoint = (ts.start + ts.end) / 2
        speaker = get_speaker_at_time(speaker_segments, midpoint)

        results.append((speaker, ts.start, ts.end, ts.text))

    return results
