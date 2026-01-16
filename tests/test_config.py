"""Tests for modules/config.py - Typed configuration system."""

import json
import os
from pathlib import Path

import pytest

from modules.config import CleanupConfig, PathsConfig, TranscribeConfig


class TestPathsConfig:
    """Tests for PathsConfig dataclass."""

    def test_default_values(self):
        """Test that all paths default to None."""
        config = PathsConfig()

        assert config.whisper_cpp_exe is None
        assert config.whisper_cpp_models is None
        assert config.output_dir is None
        assert config.oneapi_bin is None

    def test_with_all_paths(self):
        """Test creating config with all paths set."""
        config = PathsConfig(
            whisper_cpp_exe=Path("/usr/bin/whisper"),
            whisper_cpp_models=Path("/models"),
            output_dir=Path("/output"),
            oneapi_bin="/opt/intel/oneapi/bin",
        )

        assert config.whisper_cpp_exe == Path("/usr/bin/whisper")
        assert config.whisper_cpp_models == Path("/models")
        assert config.output_dir == Path("/output")
        assert config.oneapi_bin == "/opt/intel/oneapi/bin"

    def test_from_dict_with_paths(self):
        """Test creating from dictionary."""
        data = {
            "whisper_cpp_exe": "C:/whisper/whisper.exe",
            "output_dir": "C:/output",
        }

        config = PathsConfig.from_dict(data)

        assert config.whisper_cpp_exe == Path("C:/whisper/whisper.exe")
        assert config.output_dir == Path("C:/output")
        assert config.whisper_cpp_models is None

    def test_from_dict_empty(self):
        """Test creating from empty dictionary."""
        config = PathsConfig.from_dict({})

        assert config.whisper_cpp_exe is None
        assert config.output_dir is None


class TestCleanupConfig:
    """Tests for CleanupConfig dataclass."""

    def test_default_values(self):
        """Test default cleanup settings."""
        config = CleanupConfig()

        assert config.remove_duplicates is True
        assert config.remove_fillers is True
        assert config.remove_hallucinations is True
        assert config.remove_non_english is True
        assert config.min_segment_length == 3
        assert config.similarity_threshold == 0.9

    def test_custom_values(self):
        """Test custom cleanup settings."""
        config = CleanupConfig(
            remove_duplicates=False,
            remove_fillers=False,
            min_segment_length=10,
            similarity_threshold=0.8,
        )

        assert config.remove_duplicates is False
        assert config.remove_fillers is False
        assert config.min_segment_length == 10
        assert config.similarity_threshold == 0.8

    def test_from_dict(self):
        """Test creating from dictionary."""
        data = {
            "remove_duplicates": False,
            "min_segment_length": 5,
        }

        config = CleanupConfig.from_dict(data)

        assert config.remove_duplicates is False
        assert config.min_segment_length == 5
        # Defaults preserved for unspecified fields
        assert config.remove_fillers is True


class TestTranscribeConfig:
    """Tests for TranscribeConfig dataclass."""

    def test_default_values(self):
        """Test default configuration."""
        config = TranscribeConfig()

        assert config.model == "large-v3"
        assert config.huggingface_token is None
        assert config.min_speakers == 2
        assert config.max_speakers == 6
        assert isinstance(config.paths, PathsConfig)
        assert isinstance(config.cleanup, CleanupConfig)

    def test_custom_values(self):
        """Test custom configuration."""
        config = TranscribeConfig(
            model="medium",
            huggingface_token="hf_test123",
            min_speakers=1,
            max_speakers=10,
        )

        assert config.model == "medium"
        assert config.huggingface_token == "hf_test123"
        assert config.min_speakers == 1
        assert config.max_speakers == 10

    def test_from_dict(self):
        """Test creating from dictionary."""
        data = {
            "model": "small",
            "min_speakers": 3,
            "paths": {
                "output_dir": "/output",
            },
            "cleanup": {
                "remove_fillers": False,
            },
        }

        config = TranscribeConfig.from_dict(data)

        assert config.model == "small"
        assert config.min_speakers == 3
        assert config.paths.output_dir == Path("/output")
        assert config.cleanup.remove_fillers is False

    def test_from_file(self, temp_config_file):
        """Test loading from file."""
        config = TranscribeConfig.from_file(temp_config_file)

        assert config.model == "medium"
        assert config.huggingface_token == "test_token_123"
        assert config.min_speakers == 1
        assert config.max_speakers == 4

    def test_from_file_not_found(self, tmp_path):
        """Test loading from non-existent file."""
        from modules.exceptions import InvalidConfigError

        with pytest.raises(InvalidConfigError):
            TranscribeConfig.from_file(tmp_path / "nonexistent.json")

    def test_get_huggingface_token_from_config(self):
        """Test getting token from config."""
        config = TranscribeConfig(huggingface_token="hf_token_from_config")

        assert config.get_huggingface_token() == "hf_token_from_config"

    def test_get_huggingface_token_from_env(self, monkeypatch):
        """Test getting token from environment variable."""
        monkeypatch.setenv("HF_TOKEN", "hf_token_from_env")
        config = TranscribeConfig(huggingface_token=None)

        assert config.get_huggingface_token() == "hf_token_from_env"

    def test_get_huggingface_token_config_priority(self, monkeypatch):
        """Test that config token takes priority over env var."""
        monkeypatch.setenv("HF_TOKEN", "hf_token_from_env")
        config = TranscribeConfig(huggingface_token="hf_token_from_config")

        assert config.get_huggingface_token() == "hf_token_from_config"

    def test_get_huggingface_token_none(self, monkeypatch):
        """Test getting token when neither config nor env is set."""
        monkeypatch.delenv("HF_TOKEN", raising=False)
        config = TranscribeConfig(huggingface_token=None)

        assert config.get_huggingface_token() is None

    def test_to_dict(self):
        """Test converting config to dictionary."""
        config = TranscribeConfig(
            model="small",
            min_speakers=3,
        )

        data = config.to_dict()

        assert data["model"] == "small"
        assert data["min_speakers"] == 3
        assert "paths" in data
        assert "cleanup" in data

    def test_load_default(self, monkeypatch, tmp_path):
        """Test load() returns defaults when no config exists."""
        # Change to temp directory with no config.json
        monkeypatch.chdir(tmp_path)

        config = TranscribeConfig.load()

        assert config.model == "large-v3"
        assert isinstance(config, TranscribeConfig)


class TestConfigRoundtrip:
    """Tests for config serialization roundtrip."""

    def test_to_dict_from_dict_roundtrip(self):
        """Test that to_dict -> from_dict preserves data."""
        original = TranscribeConfig(
            model="medium",
            huggingface_token="test_token",
            min_speakers=1,
            max_speakers=8,
            paths=PathsConfig(
                output_dir=Path("/output"),
                whisper_cpp_exe=Path("/bin/whisper"),
            ),
            cleanup=CleanupConfig(
                remove_duplicates=False,
                min_segment_length=10,
            ),
        )

        roundtrip = TranscribeConfig.from_dict(original.to_dict())

        assert roundtrip.model == original.model
        assert roundtrip.huggingface_token == original.huggingface_token
        assert roundtrip.min_speakers == original.min_speakers
        assert roundtrip.max_speakers == original.max_speakers
        assert roundtrip.paths.output_dir == original.paths.output_dir
        assert roundtrip.cleanup.remove_duplicates == original.cleanup.remove_duplicates
