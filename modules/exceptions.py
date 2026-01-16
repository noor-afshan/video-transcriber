"""Custom exceptions for the transcription pipeline.

Exception Hierarchy:
    TranscribeError (base)
    ├── ConfigurationError
    │   ├── MissingTokenError
    │   └── InvalidConfigError
    ├── ModelError
    │   ├── ModelNotFoundError
    │   └── ModelLoadError
    ├── TranscriptionError
    │   ├── GPUUnavailableError
    │   ├── AudioConversionError
    │   └── WhisperError
    ├── DiarizationError
    └── ClassificationError
"""


class TranscribeError(Exception):
    """Base exception for all transcription pipeline errors."""
    pass


# Configuration errors
class ConfigurationError(TranscribeError):
    """Configuration-related errors."""
    pass


class MissingTokenError(ConfigurationError):
    """Required API token not provided."""

    def __init__(self, token_name: str, help_url: str | None = None):
        self.token_name = token_name
        self.help_url = help_url
        message = f"Missing required token: {token_name}"
        if help_url:
            message += f"\nGet a token at: {help_url}"
        super().__init__(message)


class InvalidConfigError(ConfigurationError):
    """Configuration file is invalid or malformed."""
    pass


# Model errors
class ModelError(TranscribeError):
    """Model-related errors."""
    pass


class ModelNotFoundError(ModelError):
    """Whisper model file not found."""

    def __init__(self, model_path: str, download_url: str | None = None):
        self.model_path = model_path
        self.download_url = download_url
        message = f"Model not found: {model_path}"
        if download_url:
            message += f"\nDownload from: {download_url}"
        super().__init__(message)


class ModelLoadError(ModelError):
    """Failed to load model into memory."""
    pass


# Transcription errors
class TranscriptionError(TranscribeError):
    """Errors during the transcription process."""
    pass


class GPUUnavailableError(TranscriptionError):
    """GPU backend (whisper.cpp) not available."""

    def __init__(self, reason: str | None = None):
        self.reason = reason
        message = "GPU backend not available"
        if reason:
            message += f": {reason}"
        super().__init__(message)


class AudioConversionError(TranscriptionError):
    """Failed to convert audio to required format (ffmpeg)."""

    def __init__(self, source_path: str, detail: str | None = None):
        self.source_path = source_path
        self.detail = detail
        message = f"Failed to convert audio: {source_path}"
        if detail:
            message += f"\n{detail}"
        super().__init__(message)


class WhisperError(TranscriptionError):
    """Whisper transcription process failed."""
    pass


# Diarization errors
class DiarizationError(TranscribeError):
    """Speaker diarization failed."""
    pass


# Classification errors
class ClassificationError(TranscribeError):
    """Frame classification failed."""
    pass
