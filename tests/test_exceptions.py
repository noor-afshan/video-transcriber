"""Tests for modules/exceptions.py - Custom exception hierarchy."""

import pytest

from modules.exceptions import (
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


class TestExceptionHierarchy:
    """Tests for exception inheritance hierarchy."""

    def test_transcribe_error_is_base(self):
        """Test that TranscribeError is the base exception."""
        assert issubclass(TranscribeError, Exception)

    def test_configuration_error_inherits_from_base(self):
        """Test ConfigurationError inheritance."""
        assert issubclass(ConfigurationError, TranscribeError)

    def test_missing_token_error_inherits_from_configuration(self):
        """Test MissingTokenError inheritance chain."""
        assert issubclass(MissingTokenError, ConfigurationError)
        assert issubclass(MissingTokenError, TranscribeError)

    def test_invalid_config_error_inherits_from_configuration(self):
        """Test InvalidConfigError inheritance."""
        assert issubclass(InvalidConfigError, ConfigurationError)

    def test_model_error_inherits_from_base(self):
        """Test ModelError inheritance."""
        assert issubclass(ModelError, TranscribeError)

    def test_model_not_found_error_inherits_from_model(self):
        """Test ModelNotFoundError inheritance chain."""
        assert issubclass(ModelNotFoundError, ModelError)
        assert issubclass(ModelNotFoundError, TranscribeError)

    def test_model_load_error_inherits_from_model(self):
        """Test ModelLoadError inheritance."""
        assert issubclass(ModelLoadError, ModelError)

    def test_transcription_error_inherits_from_base(self):
        """Test TranscriptionError inheritance."""
        assert issubclass(TranscriptionError, TranscribeError)

    def test_gpu_unavailable_error_inherits_from_transcription(self):
        """Test GPUUnavailableError inheritance chain."""
        assert issubclass(GPUUnavailableError, TranscriptionError)
        assert issubclass(GPUUnavailableError, TranscribeError)

    def test_audio_conversion_error_inherits_from_transcription(self):
        """Test AudioConversionError inheritance."""
        assert issubclass(AudioConversionError, TranscriptionError)

    def test_whisper_error_inherits_from_transcription(self):
        """Test WhisperError inheritance."""
        assert issubclass(WhisperError, TranscriptionError)

    def test_diarization_error_inherits_from_base(self):
        """Test DiarizationError inheritance."""
        assert issubclass(DiarizationError, TranscribeError)

    def test_classification_error_inherits_from_base(self):
        """Test ClassificationError inheritance."""
        assert issubclass(ClassificationError, TranscribeError)


class TestMissingTokenError:
    """Tests for MissingTokenError special fields."""

    def test_with_token_name_only(self):
        """Test creating error with just token name."""
        error = MissingTokenError("HF_TOKEN")

        assert error.token_name == "HF_TOKEN"
        assert error.help_url is None
        assert "HF_TOKEN" in str(error)

    def test_with_help_url(self):
        """Test creating error with help URL."""
        error = MissingTokenError(
            "API_KEY",
            help_url="https://example.com/get-key"
        )

        assert error.token_name == "API_KEY"
        assert error.help_url == "https://example.com/get-key"
        assert "API_KEY" in str(error)
        assert "https://example.com/get-key" in str(error)

    def test_is_catchable_as_configuration_error(self):
        """Test that error can be caught as ConfigurationError."""
        with pytest.raises(ConfigurationError):
            raise MissingTokenError("TOKEN")

    def test_is_catchable_as_transcribe_error(self):
        """Test that error can be caught as TranscribeError."""
        with pytest.raises(TranscribeError):
            raise MissingTokenError("TOKEN")


class TestModelNotFoundError:
    """Tests for ModelNotFoundError special fields."""

    def test_with_path_only(self):
        """Test creating error with just model path."""
        error = ModelNotFoundError("/path/to/model.bin")

        assert error.model_path == "/path/to/model.bin"
        assert error.download_url is None
        assert "/path/to/model.bin" in str(error)

    def test_with_download_url(self):
        """Test creating error with download URL."""
        error = ModelNotFoundError(
            "/models/large-v3.bin",
            download_url="https://huggingface.co/models"
        )

        assert error.model_path == "/models/large-v3.bin"
        assert error.download_url == "https://huggingface.co/models"
        assert "https://huggingface.co/models" in str(error)


class TestGPUUnavailableError:
    """Tests for GPUUnavailableError special fields."""

    def test_without_reason(self):
        """Test creating error without reason."""
        error = GPUUnavailableError()

        assert error.reason is None
        assert "GPU backend not available" in str(error)

    def test_with_reason(self):
        """Test creating error with reason."""
        error = GPUUnavailableError("CUDA not installed")

        assert error.reason == "CUDA not installed"
        assert "CUDA not installed" in str(error)


class TestAudioConversionError:
    """Tests for AudioConversionError special fields."""

    def test_with_path_only(self):
        """Test creating error with just source path."""
        error = AudioConversionError("/path/to/video.mp4")

        assert error.source_path == "/path/to/video.mp4"
        assert error.detail is None
        assert "/path/to/video.mp4" in str(error)

    def test_with_detail(self):
        """Test creating error with detail message."""
        error = AudioConversionError(
            "/video.mp4",
            detail="ffmpeg returned exit code 1"
        )

        assert error.source_path == "/video.mp4"
        assert error.detail == "ffmpeg returned exit code 1"
        assert "ffmpeg returned exit code 1" in str(error)


class TestExceptionCatching:
    """Tests for exception catching patterns."""

    def test_catch_all_with_base(self):
        """Test catching any transcription error with base class."""
        errors_to_test = [
            MissingTokenError("TOKEN"),
            ModelNotFoundError("/path"),
            GPUUnavailableError(),
            AudioConversionError("/path"),
            WhisperError("failed"),
            DiarizationError("failed"),
            ClassificationError("failed"),
        ]

        for error in errors_to_test:
            with pytest.raises(TranscribeError):
                raise error

    def test_catch_model_errors_specifically(self):
        """Test catching model-related errors."""
        model_errors = [
            ModelNotFoundError("/path"),
            ModelLoadError("out of memory"),
        ]

        for error in model_errors:
            with pytest.raises(ModelError):
                raise error

    def test_catch_transcription_errors_specifically(self):
        """Test catching transcription-related errors."""
        transcription_errors = [
            GPUUnavailableError(),
            AudioConversionError("/path"),
            WhisperError("failed"),
        ]

        for error in transcription_errors:
            with pytest.raises(TranscriptionError):
                raise error
