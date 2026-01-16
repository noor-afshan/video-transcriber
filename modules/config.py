"""Typed configuration for the transcription pipeline."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

from .exceptions import InvalidConfigError


@dataclass
class PathsConfig:
    """Configuration for file paths."""

    whisper_cpp_exe: Path | None = None
    whisper_cpp_models: Path | None = None
    output_dir: Path | None = None
    oneapi_bin: str | None = None

    @classmethod
    def from_dict(cls, data: dict) -> PathsConfig:
        """Create from dictionary, converting strings to Paths."""
        return cls(
            whisper_cpp_exe=Path(data["whisper_cpp_exe"]) if data.get("whisper_cpp_exe") else None,
            whisper_cpp_models=Path(data["whisper_cpp_models"]) if data.get("whisper_cpp_models") else None,
            output_dir=Path(data["output_dir"]) if data.get("output_dir") else None,
            oneapi_bin=data.get("oneapi_bin"),
        )


@dataclass
class CleanupConfig:
    """Configuration for transcript cleanup."""

    remove_duplicates: bool = True
    remove_fillers: bool = True
    remove_hallucinations: bool = True
    remove_non_english: bool = True
    min_segment_length: int = 3
    similarity_threshold: float = 0.9

    @classmethod
    def from_dict(cls, data: dict) -> CleanupConfig:
        """Create from dictionary with defaults for missing keys."""
        defaults = cls()
        return cls(
            remove_duplicates=data.get("remove_duplicates", defaults.remove_duplicates),
            remove_fillers=data.get("remove_fillers", defaults.remove_fillers),
            remove_hallucinations=data.get("remove_hallucinations", defaults.remove_hallucinations),
            remove_non_english=data.get("remove_non_english", defaults.remove_non_english),
            min_segment_length=data.get("min_segment_length", defaults.min_segment_length),
            similarity_threshold=data.get("similarity_threshold", defaults.similarity_threshold),
        )


@dataclass
class TranscribeConfig:
    """
    Main configuration for the transcription pipeline.

    Attributes:
        model: Whisper model size (tiny, base, small, medium, large-v3, turbo)
        huggingface_token: Token for pyannote speaker diarization
        min_speakers: Minimum expected speakers for diarization
        max_speakers: Maximum expected speakers for diarization
        paths: File path configuration
        cleanup: Transcript cleanup configuration
    """

    model: str = "large-v3"
    huggingface_token: str | None = None
    min_speakers: int = 2
    max_speakers: int = 6
    paths: PathsConfig = field(default_factory=PathsConfig)
    cleanup: CleanupConfig = field(default_factory=CleanupConfig)

    # Valid model sizes
    VALID_MODELS = ["tiny", "base", "small", "medium", "large-v3", "turbo"]

    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.model not in self.VALID_MODELS:
            raise InvalidConfigError(
                f"Invalid model: {self.model}. Valid options: {self.VALID_MODELS}"
            )
        if self.min_speakers < 1:
            raise InvalidConfigError("min_speakers must be at least 1")
        if self.max_speakers < self.min_speakers:
            raise InvalidConfigError("max_speakers must be >= min_speakers")

    @classmethod
    def from_dict(cls, data: dict) -> TranscribeConfig:
        """
        Create configuration from a dictionary.

        Handles nested 'paths' and 'cleanup' sections.
        """
        paths_data = data.get("paths", {})
        cleanup_data = data.get("cleanup", {})

        return cls(
            model=data.get("model", "large-v3"),
            huggingface_token=data.get("huggingface_token"),
            min_speakers=data.get("min_speakers", 2),
            max_speakers=data.get("max_speakers", 6),
            paths=PathsConfig.from_dict(paths_data) if paths_data else PathsConfig(),
            cleanup=CleanupConfig.from_dict(cleanup_data) if cleanup_data else CleanupConfig(),
        )

    @classmethod
    def from_file(cls, path: Path | str) -> TranscribeConfig:
        """
        Load configuration from a JSON file.

        Args:
            path: Path to the JSON configuration file

        Returns:
            TranscribeConfig instance

        Raises:
            InvalidConfigError: If the file cannot be read or parsed
        """
        path = Path(path)

        if not path.exists():
            raise InvalidConfigError(f"Configuration file not found: {path}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise InvalidConfigError(f"Invalid JSON in config file: {e}")
        except OSError as e:
            raise InvalidConfigError(f"Cannot read config file: {e}")

        return cls.from_dict(data)

    @classmethod
    def load(cls, config_path: Path | str | None = None) -> TranscribeConfig:
        """
        Load configuration with fallback to default locations.

        Search order:
        1. Explicit config_path if provided
        2. config.json in current working directory
        3. config.json in script directory (modules/../config.json)
        4. Default configuration

        Args:
            config_path: Optional explicit path to config file

        Returns:
            TranscribeConfig instance
        """
        # Try explicit path first
        if config_path:
            return cls.from_file(config_path)

        # Try current directory
        cwd_config = Path.cwd() / "config.json"
        if cwd_config.exists():
            return cls.from_file(cwd_config)

        # Try script directory (modules/../config.json)
        script_config = Path(__file__).parent.parent / "config.json"
        if script_config.exists():
            return cls.from_file(script_config)

        # Return defaults
        return cls()

    def get_huggingface_token(self) -> str | None:
        """Get HuggingFace token from config or environment."""
        return self.huggingface_token or os.environ.get("HF_TOKEN")

    def to_dict(self) -> dict:
        """Convert configuration to dictionary (for serialization)."""
        return {
            "model": self.model,
            "huggingface_token": self.huggingface_token,
            "min_speakers": self.min_speakers,
            "max_speakers": self.max_speakers,
            "paths": {
                "whisper_cpp_exe": str(self.paths.whisper_cpp_exe) if self.paths.whisper_cpp_exe else None,
                "whisper_cpp_models": str(self.paths.whisper_cpp_models) if self.paths.whisper_cpp_models else None,
                "output_dir": str(self.paths.output_dir) if self.paths.output_dir else None,
                "oneapi_bin": self.paths.oneapi_bin,
            },
            "cleanup": {
                "remove_duplicates": self.cleanup.remove_duplicates,
                "remove_fillers": self.cleanup.remove_fillers,
                "remove_hallucinations": self.cleanup.remove_hallucinations,
                "remove_non_english": self.cleanup.remove_non_english,
                "min_segment_length": self.cleanup.min_segment_length,
                "similarity_threshold": self.cleanup.similarity_threshold,
            },
        }
