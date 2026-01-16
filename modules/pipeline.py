"""Composable transcription pipeline architecture.

Provides a flexible pipeline pattern for video/audio transcription with
optional speaker diarization and cleanup stages.

Example usage:
    from modules.pipeline import TranscriptionPipeline, TranscribeStage, DiarizeStage, CleanupStage
    from modules.config import TranscribeConfig

    config = TranscribeConfig.load()

    pipeline = (TranscriptionPipeline()
        .add_stage(TranscribeStage(config))
        .add_stage(DiarizeStage(config))
        .add_stage(CleanupStage(config)))

    segments = pipeline.run(Path("video.mp4"))
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from .config import TranscribeConfig
    from .transcriber import TranscriptSegment
    from .types import DiarizedSegment


class PipelineStage(ABC):
    """
    Abstract base class for pipeline stages.

    Each stage transforms input data and passes it to the next stage.
    Stages should be stateless and reusable.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name for this stage."""
        pass

    @abstractmethod
    def process(self, data: Any) -> Any:
        """
        Process input data and return transformed output.

        Args:
            data: Input from previous stage (or initial input for first stage)

        Returns:
            Transformed data for next stage
        """
        pass


class TranscribeStage(PipelineStage):
    """
    Transcription stage - converts audio/video to text segments.

    Input: Path to audio/video file
    Output: list[TranscriptSegment]
    """

    def __init__(
        self,
        config: TranscribeConfig | None = None,
        model_size: str | None = None,
        use_gpu: bool = True,
        show_progress: bool = True,
        debug: bool = False,
    ):
        """
        Initialize transcription stage.

        Args:
            config: TranscribeConfig for path settings (optional)
            model_size: Override model size (default: from config or "large-v3")
            use_gpu: Try GPU backend first if available
            show_progress: Show real-time progress
            debug: Show debug output
        """
        self._config = config
        self._model_size = model_size
        self._use_gpu = use_gpu
        self._show_progress = show_progress
        self._debug = debug

    @property
    def name(self) -> str:
        return "Transcribe"

    def process(self, data: Path | str) -> list[TranscriptSegment]:
        """
        Transcribe audio/video file.

        Args:
            data: Path to audio/video file

        Returns:
            List of TranscriptSegment with timing and text
        """
        # Lazy imports to keep CLI startup fast
        from .transcriber import (
            CpuTranscriber,
            GpuTranscriber,
            TranscriptSegment,
            is_gpu_available,
        )

        audio_path = Path(data)

        # Get configuration values
        model_size = self._model_size
        paths_config = None

        if self._config:
            model_size = model_size or self._config.model
            paths_config = self._config.paths

        model_size = model_size or "large-v3"

        # Extract path settings
        whisper_exe = None
        models_dir = None
        oneapi_bin = None

        if paths_config:
            whisper_exe = paths_config.whisper_cpp_exe
            models_dir = paths_config.whisper_cpp_models
            oneapi_bin = paths_config.oneapi_bin

        # Try GPU first, fallback to CPU
        if self._use_gpu and is_gpu_available(whisper_exe):
            try:
                transcriber = GpuTranscriber(
                    model_size=model_size,
                    whisper_exe=whisper_exe,
                    models_dir=models_dir,
                    oneapi_bin=oneapi_bin,
                )
                return transcriber.transcribe_to_list(
                    audio_path,
                    show_progress=self._show_progress,
                    debug=self._debug,
                )
            except Exception as e:
                print(f"WARNING: GPU transcription failed: {e}")
                print("Falling back to CPU...\n")

        # CPU fallback
        if not self._use_gpu:
            print("Using CPU backend (faster-whisper)...")

        transcriber = CpuTranscriber(model_size=model_size)
        return transcriber.transcribe_to_list(audio_path)


class DiarizeStage(PipelineStage):
    """
    Speaker diarization stage - assigns speakers to transcript segments.

    Input: list[TranscriptSegment]
    Output: list[DiarizedSegment]

    Requires audio_path to be set before processing (via set_audio_path or pipeline context).
    """

    def __init__(
        self,
        config: TranscribeConfig | None = None,
        hf_token: str | None = None,
        min_speakers: int = 2,
        max_speakers: int = 6,
        enabled: bool = True,
    ):
        """
        Initialize diarization stage.

        Args:
            config: TranscribeConfig for token and speaker settings
            hf_token: HuggingFace token (overrides config)
            min_speakers: Minimum expected speakers
            max_speakers: Maximum expected speakers
            enabled: Whether diarization is enabled
        """
        self._config = config
        self._hf_token = hf_token
        self._min_speakers = min_speakers
        self._max_speakers = max_speakers
        self._enabled = enabled
        self._audio_path: Path | None = None

    @property
    def name(self) -> str:
        return "Diarize"

    def set_audio_path(self, path: Path | str) -> DiarizeStage:
        """Set the audio path for diarization (needed for speaker identification)."""
        self._audio_path = Path(path)
        return self

    def process(self, data: list[TranscriptSegment]) -> list[DiarizedSegment]:
        """
        Assign speakers to transcript segments.

        Args:
            data: List of TranscriptSegment from transcription

        Returns:
            List of DiarizedSegment with speaker attribution
        """
        import os

        from .diarizer import (
            Diarizer,
            assign_speakers_to_transcript,
            segments_without_speakers,
        )

        # If disabled, return segments without speaker identification
        if not self._enabled:
            return segments_without_speakers(data)

        # Resolve HuggingFace token
        hf_token = self._hf_token
        if not hf_token and self._config:
            hf_token = self._config.get_huggingface_token()
        if not hf_token:
            hf_token = os.environ.get("HF_TOKEN")

        if not hf_token:
            print("\nWARNING: No HuggingFace token found. Skipping speaker diarization.")
            print("Set HF_TOKEN environment variable or add 'huggingface_token' to config.json")
            print("Get a token at: https://huggingface.co/settings/tokens\n")
            return segments_without_speakers(data)

        if not self._audio_path:
            print("\nWARNING: Audio path not set for diarization. Skipping speaker identification.")
            return segments_without_speakers(data)

        # Get speaker count settings
        min_speakers = self._min_speakers
        max_speakers = self._max_speakers

        if self._config:
            min_speakers = self._config.min_speakers
            max_speakers = self._config.max_speakers

        try:
            diarizer = Diarizer(
                hf_token=hf_token,
                min_speakers=min_speakers,
                max_speakers=max_speakers,
            )
            speaker_segments = diarizer.diarize(self._audio_path)
            return assign_speakers_to_transcript(data, speaker_segments)

        except Exception as e:
            print(f"\nWARNING: Diarization failed: {e}")
            print("Continuing without speaker identification.\n")
            return segments_without_speakers(data)


class CleanupStage(PipelineStage):
    """
    Cleanup stage - removes hallucinations, duplicates, and fillers.

    Input: list[DiarizedSegment]
    Output: list[DiarizedSegment]
    """

    def __init__(
        self,
        config: TranscribeConfig | None = None,
        remove_duplicates: bool = True,
        remove_fillers: bool = True,
        remove_hallucinations: bool = True,
        remove_non_english: bool = True,
        min_segment_length: int = 3,
        similarity_threshold: float = 0.9,
        enabled: bool = True,
    ):
        """
        Initialize cleanup stage.

        Args:
            config: TranscribeConfig for cleanup settings
            remove_duplicates: Remove consecutive duplicate lines
            remove_fillers: Remove short filler words
            remove_hallucinations: Remove known Whisper hallucination patterns
            remove_non_english: Remove segments with non-English characters
            min_segment_length: Minimum character length for segments
            similarity_threshold: Threshold for duplicate detection (0.0-1.0)
            enabled: Whether cleanup is enabled
        """
        self._config = config
        self._remove_duplicates = remove_duplicates
        self._remove_fillers = remove_fillers
        self._remove_hallucinations = remove_hallucinations
        self._remove_non_english = remove_non_english
        self._min_segment_length = min_segment_length
        self._similarity_threshold = similarity_threshold
        self._enabled = enabled

    @property
    def name(self) -> str:
        return "Cleanup"

    def process(self, data: list[DiarizedSegment]) -> list[DiarizedSegment]:
        """
        Clean transcript segments.

        Args:
            data: List of DiarizedSegment

        Returns:
            Cleaned list with artifacts removed
        """
        if not self._enabled:
            return data

        from .cleaner import TranscriptCleaner

        # Get cleanup settings from config or use constructor values
        remove_duplicates = self._remove_duplicates
        remove_fillers = self._remove_fillers
        remove_hallucinations = self._remove_hallucinations
        remove_non_english = self._remove_non_english
        min_segment_length = self._min_segment_length
        similarity_threshold = self._similarity_threshold

        if self._config and self._config.cleanup:
            cleanup = self._config.cleanup
            remove_duplicates = cleanup.remove_duplicates
            remove_fillers = cleanup.remove_fillers
            remove_hallucinations = cleanup.remove_hallucinations
            remove_non_english = cleanup.remove_non_english
            min_segment_length = cleanup.min_segment_length
            similarity_threshold = cleanup.similarity_threshold

        cleaner = TranscriptCleaner(
            remove_duplicates=remove_duplicates,
            remove_fillers=remove_fillers,
            remove_hallucinations=remove_hallucinations,
            remove_non_english=remove_non_english,
            min_segment_length=min_segment_length,
            similarity_threshold=similarity_threshold,
        )

        return cleaner.clean(data)


class TranscriptionPipeline:
    """
    Composable pipeline for audio/video transcription.

    Stages are executed in order, with each stage's output becoming
    the next stage's input.

    Example:
        pipeline = (TranscriptionPipeline()
            .add_stage(TranscribeStage(config))
            .add_stage(DiarizeStage(config))
            .add_stage(CleanupStage(config)))

        segments = pipeline.run(Path("video.mp4"))
    """

    def __init__(self):
        """Initialize an empty pipeline."""
        self._stages: list[PipelineStage] = []
        self._on_stage_start: Callable[[str], None] | None = None
        self._on_stage_complete: Callable[[str, Any], None] | None = None

    def add_stage(self, stage: PipelineStage) -> TranscriptionPipeline:
        """
        Add a stage to the pipeline.

        Args:
            stage: PipelineStage to add

        Returns:
            Self for method chaining
        """
        self._stages.append(stage)
        return self

    def on_stage_start(self, callback: Callable[[str], None]) -> TranscriptionPipeline:
        """
        Set callback for when a stage starts.

        Args:
            callback: Function called with stage name

        Returns:
            Self for method chaining
        """
        self._on_stage_start = callback
        return self

    def on_stage_complete(self, callback: Callable[[str, Any], None]) -> TranscriptionPipeline:
        """
        Set callback for when a stage completes.

        Args:
            callback: Function called with (stage_name, result)

        Returns:
            Self for method chaining
        """
        self._on_stage_complete = callback
        return self

    @property
    def stages(self) -> list[PipelineStage]:
        """Get the list of stages."""
        return self._stages.copy()

    def run(self, audio_path: Path | str) -> list[DiarizedSegment]:
        """
        Run the pipeline on an audio/video file.

        Args:
            audio_path: Path to audio/video file

        Returns:
            List of DiarizedSegment from the final stage
        """
        audio_path = Path(audio_path)
        data: Any = audio_path

        for stage in self._stages:
            # Set audio path for diarization stage (needs original file)
            if isinstance(stage, DiarizeStage):
                stage.set_audio_path(audio_path)

            # Notify stage start
            if self._on_stage_start:
                self._on_stage_start(stage.name)

            # Process
            data = stage.process(data)

            # Notify stage complete
            if self._on_stage_complete:
                self._on_stage_complete(stage.name, data)

        return data


def create_default_pipeline(
    config: TranscribeConfig | None = None,
    use_gpu: bool = True,
    enable_diarization: bool = True,
    enable_cleanup: bool = True,
    show_progress: bool = True,
    debug: bool = False,
) -> TranscriptionPipeline:
    """
    Create a standard transcription pipeline.

    This is a convenience function that creates a typical pipeline with
    transcription, optional diarization, and optional cleanup.

    Args:
        config: TranscribeConfig for settings
        use_gpu: Try GPU backend first
        enable_diarization: Enable speaker identification
        enable_cleanup: Enable transcript cleanup
        show_progress: Show real-time progress
        debug: Show debug output

    Returns:
        Configured TranscriptionPipeline
    """
    pipeline = TranscriptionPipeline()

    # Always add transcription
    pipeline.add_stage(TranscribeStage(
        config=config,
        use_gpu=use_gpu,
        show_progress=show_progress,
        debug=debug,
    ))

    # Add diarization (handles disabled state internally)
    pipeline.add_stage(DiarizeStage(
        config=config,
        enabled=enable_diarization,
    ))

    # Add cleanup (handles disabled state internally)
    pipeline.add_stage(CleanupStage(
        config=config,
        enabled=enable_cleanup,
    ))

    return pipeline
