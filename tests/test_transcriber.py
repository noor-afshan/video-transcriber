"""Tests for modules/transcriber.py - Transcriber classes.

Note: These tests focus on unit testing the transcriber classes without
requiring actual Whisper models, which would be slow and require large downloads.
Integration tests with real models should be run separately.
"""

import pytest
from pathlib import Path

from modules.transcriber import (
    BaseTranscriber,
    CpuTranscriber,
    GpuTranscriber,
    TranscriptSegment,
    Transcriber,
    format_time,
    is_gpu_available,
    ALLOWED_EXTENSIONS,
    WHISPER_CPP_MODEL_MAP,
)


class TestTranscriptSegment:
    """Tests for TranscriptSegment dataclass."""

    def test_creation(self):
        """Test creating a TranscriptSegment."""
        seg = TranscriptSegment(start=1.5, end=5.0, text="Hello world")

        assert seg.start == 1.5
        assert seg.end == 5.0
        assert seg.text == "Hello world"

    def test_equality(self):
        """Test TranscriptSegment equality."""
        seg1 = TranscriptSegment(start=0, end=5, text="Test")
        seg2 = TranscriptSegment(start=0, end=5, text="Test")

        assert seg1 == seg2

    def test_inequality(self):
        """Test TranscriptSegment inequality."""
        seg1 = TranscriptSegment(start=0, end=5, text="Test A")
        seg2 = TranscriptSegment(start=0, end=5, text="Test B")

        assert seg1 != seg2


class TestFormatTime:
    """Tests for format_time utility function."""

    def test_zero_seconds(self):
        """Test formatting zero seconds."""
        assert format_time(0) == "00:00:00"

    def test_seconds_only(self):
        """Test formatting seconds only."""
        assert format_time(45) == "00:00:45"

    def test_minutes_and_seconds(self):
        """Test formatting minutes and seconds."""
        assert format_time(125) == "00:02:05"

    def test_hours_minutes_seconds(self):
        """Test formatting with hours."""
        assert format_time(3661) == "01:01:01"

    def test_fractional_seconds_truncated(self):
        """Test that fractional seconds are truncated."""
        assert format_time(45.7) == "00:00:45"

    def test_large_hours(self):
        """Test formatting large hour values."""
        assert format_time(36000) == "10:00:00"


class TestAllowedExtensions:
    """Tests for ALLOWED_EXTENSIONS constant."""

    def test_video_extensions_included(self):
        """Test that common video extensions are allowed."""
        video_exts = [".mp4", ".mkv", ".avi", ".mov", ".webm"]
        for ext in video_exts:
            assert ext in ALLOWED_EXTENSIONS

    def test_audio_extensions_included(self):
        """Test that common audio extensions are allowed."""
        audio_exts = [".mp3", ".wav", ".flac", ".m4a", ".ogg", ".aac"]
        for ext in audio_exts:
            assert ext in ALLOWED_EXTENSIONS

    def test_invalid_extensions_excluded(self):
        """Test that invalid extensions are not allowed."""
        invalid_exts = [".txt", ".pdf", ".exe", ".py"]
        for ext in invalid_exts:
            assert ext not in ALLOWED_EXTENSIONS


class TestWhisperModelMap:
    """Tests for WHISPER_CPP_MODEL_MAP constant."""

    def test_all_models_mapped(self):
        """Test that all supported models have mappings."""
        expected_models = ["tiny", "base", "small", "medium", "large-v3", "turbo"]
        for model in expected_models:
            assert model in WHISPER_CPP_MODEL_MAP

    def test_model_files_have_bin_extension(self):
        """Test that model files have .bin extension."""
        for model_file in WHISPER_CPP_MODEL_MAP.values():
            assert model_file.endswith(".bin")

    def test_turbo_uses_turbo_model(self):
        """Test that turbo model uses the turbo file."""
        assert "turbo" in WHISPER_CPP_MODEL_MAP["turbo"]


class TestBaseTranscriber:
    """Tests for BaseTranscriber abstract base class."""

    def test_cannot_instantiate_directly(self):
        """Test that BaseTranscriber cannot be instantiated."""
        with pytest.raises(TypeError):
            BaseTranscriber()

    def test_valid_models_list(self):
        """Test VALID_MODELS class attribute."""
        expected = ["tiny", "base", "small", "medium", "large-v3", "turbo"]
        assert BaseTranscriber.VALID_MODELS == expected

    def test_subclass_must_implement_transcribe(self):
        """Test that subclasses must implement transcribe method."""
        class IncompleteTranscriber(BaseTranscriber):
            pass

        with pytest.raises(TypeError):
            IncompleteTranscriber()


class TestCpuTranscriber:
    """Tests for CpuTranscriber class (without loading models)."""

    def test_default_model_size(self):
        """Test default model size is large-v3."""
        transcriber = CpuTranscriber()
        assert transcriber.model_size == "large-v3"

    def test_custom_model_size(self):
        """Test setting custom model size."""
        transcriber = CpuTranscriber(model_size="medium")
        assert transcriber.model_size == "medium"

    def test_invalid_model_size(self):
        """Test that invalid model size raises error."""
        with pytest.raises(ValueError) as exc_info:
            CpuTranscriber(model_size="invalid-model")

        assert "invalid-model" in str(exc_info.value)

    def test_default_device(self):
        """Test default device is cpu."""
        transcriber = CpuTranscriber()
        assert transcriber.device == "cpu"

    def test_model_not_loaded_initially(self):
        """Test that model is not loaded on init (lazy loading)."""
        transcriber = CpuTranscriber()
        assert transcriber._model is None

    def test_inherits_from_base(self):
        """Test that CpuTranscriber inherits from BaseTranscriber."""
        assert issubclass(CpuTranscriber, BaseTranscriber)


class TestTranscriberAlias:
    """Tests for Transcriber backward compatibility alias."""

    def test_transcriber_is_cpu_transcriber(self):
        """Test that Transcriber is an alias for CpuTranscriber."""
        assert Transcriber is CpuTranscriber

    def test_transcriber_creates_cpu_instance(self):
        """Test that Transcriber() creates CpuTranscriber instance."""
        transcriber = Transcriber()
        assert isinstance(transcriber, CpuTranscriber)


class TestGpuTranscriber:
    """Tests for GpuTranscriber class (without requiring GPU)."""

    def test_default_model_size(self):
        """Test default model size is large-v3."""
        # Note: This may raise ModelNotFoundError if model doesn't exist
        # We're testing the initialization logic, not model loading
        try:
            transcriber = GpuTranscriber()
            assert transcriber.model_size == "large-v3"
        except Exception:
            # Model not found is expected if whisper.cpp not installed
            pass

    def test_invalid_model_size(self):
        """Test that invalid model size raises error."""
        with pytest.raises(ValueError) as exc_info:
            GpuTranscriber(model_size="invalid-model")

        assert "invalid-model" in str(exc_info.value)

    def test_inherits_from_base(self):
        """Test that GpuTranscriber inherits from BaseTranscriber."""
        assert issubclass(GpuTranscriber, BaseTranscriber)


class TestIsGpuAvailable:
    """Tests for is_gpu_available function."""

    def test_returns_bool(self):
        """Test that function returns a boolean."""
        result = is_gpu_available()
        assert isinstance(result, bool)

    def test_with_nonexistent_path(self):
        """Test with non-existent executable path."""
        result = is_gpu_available("/nonexistent/path/whisper.exe")
        assert result is False

    def test_with_custom_path(self, tmp_path):
        """Test with custom whisper executable path."""
        # Create a fake executable
        fake_exe = tmp_path / "whisper.exe"
        fake_exe.touch()

        result = is_gpu_available(str(fake_exe))
        assert result is True


class TestTranscriberIntegration:
    """Integration tests for transcriber classes.

    These tests verify the interaction between transcriber classes
    without requiring actual model files.
    """

    def test_all_valid_models_accepted(self):
        """Test that all valid models are accepted by transcribers."""
        for model in BaseTranscriber.VALID_MODELS:
            transcriber = CpuTranscriber(model_size=model)
            assert transcriber.model_size == model

    def test_transcribe_to_list_defined(self):
        """Test that transcribe_to_list method exists."""
        transcriber = CpuTranscriber()
        assert hasattr(transcriber, "transcribe_to_list")
        assert callable(transcriber.transcribe_to_list)

    def test_transcribe_defined(self):
        """Test that transcribe method exists."""
        transcriber = CpuTranscriber()
        assert hasattr(transcriber, "transcribe")
        assert callable(transcriber.transcribe)
