"""Pytest configuration and shared fixtures for transcription tests."""

import sys
from pathlib import Path

import pytest

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def sample_transcript_segments():
    """Sample TranscriptSegment objects for testing."""
    from modules.transcriber import TranscriptSegment

    return [
        TranscriptSegment(start=0.0, end=5.0, text="Hello, how are you?"),
        TranscriptSegment(start=5.0, end=10.0, text="I'm doing well, thanks."),
        TranscriptSegment(start=10.0, end=15.0, text="That's great to hear."),
    ]


@pytest.fixture
def sample_diarized_segments():
    """Sample DiarizedSegment objects for testing."""
    from modules.types import DiarizedSegment

    return [
        DiarizedSegment(start=0.0, end=5.0, text="Hello, how are you?", speaker="Speaker 1"),
        DiarizedSegment(start=5.0, end=10.0, text="I'm doing well, thanks.", speaker="Speaker 2"),
        DiarizedSegment(start=10.0, end=15.0, text="That's great to hear.", speaker="Speaker 1"),
    ]


@pytest.fixture
def sample_speaker_segments():
    """Sample SpeakerSegment objects for testing."""
    from modules.diarizer import SpeakerSegment

    return [
        SpeakerSegment(start=0.0, end=6.0, speaker="Speaker 1"),
        SpeakerSegment(start=6.0, end=12.0, speaker="Speaker 2"),
        SpeakerSegment(start=12.0, end=18.0, speaker="Speaker 1"),
    ]


@pytest.fixture
def temp_config_file(tmp_path):
    """Create a temporary config.json file."""
    import json

    config = {
        "model": "medium",
        "huggingface_token": "test_token_123",
        "min_speakers": 1,
        "max_speakers": 4,
        "paths": {
            "output_dir": str(tmp_path / "output"),
        },
        "cleanup": {
            "remove_duplicates": True,
            "remove_fillers": False,
            "min_segment_length": 5,
        },
    }

    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config))
    return config_path


@pytest.fixture
def segments_with_hallucinations():
    """Segments containing common Whisper hallucination patterns."""
    from modules.types import DiarizedSegment

    return [
        DiarizedSegment(start=0.0, end=5.0, text="This is real content.", speaker="Speaker 1"),
        DiarizedSegment(start=5.0, end=10.0, text="Thanks for watching!", speaker="Speaker 1"),
        DiarizedSegment(start=10.0, end=15.0, text="More real content here.", speaker="Speaker 2"),
        DiarizedSegment(start=15.0, end=20.0, text="Don't forget to subscribe!", speaker="Speaker 1"),
        DiarizedSegment(start=20.0, end=25.0, text="[music]", speaker="Unknown"),
    ]


@pytest.fixture
def segments_with_duplicates():
    """Segments containing near-duplicates."""
    from modules.types import DiarizedSegment

    return [
        DiarizedSegment(start=0.0, end=5.0, text="Hello there.", speaker="Speaker 1"),
        DiarizedSegment(start=5.0, end=10.0, text="Hello there.", speaker="Speaker 1"),  # Exact duplicate
        DiarizedSegment(start=10.0, end=15.0, text="Hello there!", speaker="Speaker 1"),  # Near duplicate
        DiarizedSegment(start=15.0, end=20.0, text="Something different.", speaker="Speaker 2"),
    ]


@pytest.fixture
def segments_with_fillers():
    """Segments containing filler words."""
    from modules.types import DiarizedSegment

    return [
        DiarizedSegment(start=0.0, end=2.0, text="Um", speaker="Speaker 1"),
        DiarizedSegment(start=2.0, end=5.0, text="So I was thinking...", speaker="Speaker 1"),
        DiarizedSegment(start=5.0, end=7.0, text="Uh", speaker="Speaker 1"),
        DiarizedSegment(start=7.0, end=12.0, text="We should proceed with the plan.", speaker="Speaker 1"),
        DiarizedSegment(start=12.0, end=14.0, text="Yeah", speaker="Speaker 2"),
    ]
