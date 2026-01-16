"""Transcription modules for video transcription with speaker diarization.

This package provides a complete pipeline for transcribing audio/video files
with optional speaker identification and transcript cleanup.

Quick Start:
    from modules import TranscribeConfig, create_default_pipeline

    config = TranscribeConfig.load()
    pipeline = create_default_pipeline(config=config)
    segments = pipeline.run("video.mp4")

    for seg in segments:
        print(f"[{seg.start:.1f}s] {seg.speaker}: {seg.text}")

Core Classes:
    - Transcriber: CPU transcription (faster-whisper)
    - GpuTranscriber: GPU transcription (whisper.cpp + Intel Arc)
    - Diarizer: Speaker identification (pyannote-audio)
    - TranscriptCleaner: Post-processing cleanup

Pipeline Classes:
    - TranscriptionPipeline: Composable pipeline orchestrator
    - TranscribeStage, DiarizeStage, CleanupStage: Pipeline stages

Data Types:
    - TranscriptSegment: Raw transcription segment (start, end, text)
    - DiarizedSegment: Segment with speaker attribution
    - SpeakerSegment: Speaker timing segment

Configuration:
    - TranscribeConfig: Main configuration dataclass
    - PathsConfig: Path settings (whisper.cpp, models, output)
    - CleanupConfig: Cleanup behavior settings

Exceptions:
    - TranscribeError: Base exception for all errors
    - ModelNotFoundError, AudioConversionError, etc.
"""

# Data types
from .types import DiarizedSegment

# Transcriber classes and utilities
from .transcriber import (
    BaseTranscriber,
    CpuTranscriber,
    GpuTranscriber,
    Transcriber,  # Backward compat alias for CpuTranscriber
    TranscriptSegment,
    format_time,
    is_gpu_available,
)

# Diarizer classes and utilities
from .diarizer import (
    Diarizer,
    SpeakerSegment,
    assign_speakers_to_transcript,
    get_speaker_at_time,
    segments_without_speakers,
)

# Cleaner
from .cleaner import TranscriptCleaner

# Configuration
from .config import (
    CleanupConfig,
    PathsConfig,
    TranscribeConfig,
)

# Pipeline architecture
from .pipeline import (
    CleanupStage,
    DiarizeStage,
    PipelineStage,
    TranscribeStage,
    TranscriptionPipeline,
    create_default_pipeline,
)

# Exceptions
from .exceptions import (
    AudioConversionError,
    ClassificationError,
    ConfigurationError,
    DiarizationError,
    GPUUnavailableError,
    InvalidConfigError,
    MissingTokenError,
    ModelError,
    ModelLoadError,
    ModelNotFoundError,
    TranscribeError,
    TranscriptionError,
    WhisperError,
)

__all__ = [
    # Data types
    "DiarizedSegment",
    "TranscriptSegment",
    "SpeakerSegment",
    # Transcribers
    "BaseTranscriber",
    "CpuTranscriber",
    "GpuTranscriber",
    "Transcriber",
    "is_gpu_available",
    "format_time",
    # Diarizer
    "Diarizer",
    "assign_speakers_to_transcript",
    "segments_without_speakers",
    "get_speaker_at_time",
    # Cleaner
    "TranscriptCleaner",
    # Configuration
    "TranscribeConfig",
    "PathsConfig",
    "CleanupConfig",
    # Pipeline
    "PipelineStage",
    "TranscribeStage",
    "DiarizeStage",
    "CleanupStage",
    "TranscriptionPipeline",
    "create_default_pipeline",
    # Exceptions
    "TranscribeError",
    "ConfigurationError",
    "MissingTokenError",
    "InvalidConfigError",
    "ModelError",
    "ModelNotFoundError",
    "ModelLoadError",
    "TranscriptionError",
    "GPUUnavailableError",
    "AudioConversionError",
    "WhisperError",
    "DiarizationError",
    "ClassificationError",
]
