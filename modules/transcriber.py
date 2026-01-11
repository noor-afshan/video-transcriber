"""Whisper transcription module with GPU (whisper.cpp) and CPU (faster-whisper) backends."""

import os
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


@dataclass
class TranscriptSegment:
    """A single transcription segment with timing."""
    start: float
    end: float
    text: str


# Default whisper.cpp paths (fallbacks if not configured)
_DEFAULT_WHISPER_EXE = Path(r"C:\whisper.cpp\bin\whisper-cli.exe")
_DEFAULT_WHISPER_MODELS = Path(r"C:\whisper.cpp\models")
_DEFAULT_ONEAPI_BIN = r"C:\Program Files (x86)\Intel\oneAPI"


def _resolve_path(config_value: str | Path | None, env_var: str, default: Path) -> Path:
    """Resolve path from config, environment variable, or default."""
    if config_value:
        return Path(config_value)
    env_value = os.environ.get(env_var)
    if env_value:
        return Path(env_value)
    return default


def _find_oneapi_bin(config_value: str | None) -> str | None:
    """Find Intel oneAPI bin directory, auto-detecting version if needed."""
    if config_value and os.path.exists(config_value):
        return config_value

    env_value = os.environ.get("ONEAPI_BIN")
    if env_value and os.path.exists(env_value):
        return env_value

    # Auto-detect latest version
    oneapi_base = Path(_DEFAULT_ONEAPI_BIN)
    if oneapi_base.exists():
        # Find latest version directory
        versions = sorted(
            [d for d in oneapi_base.iterdir() if d.is_dir() and (d / "bin").exists()],
            reverse=True
        )
        if versions:
            return str(versions[0] / "bin")
    return None

# Model mapping: script model names -> whisper.cpp model files
WHISPER_CPP_MODEL_MAP = {
    "tiny": "ggml-tiny.bin",
    "base": "ggml-base.bin",
    "small": "ggml-small.bin",
    "medium": "ggml-medium.bin",
    "large-v3": "ggml-large-v3-turbo.bin",  # Use turbo for speed
    "turbo": "ggml-large-v3-turbo.bin",
}


# Allowed audio/video extensions for transcription
ALLOWED_EXTENSIONS = {
    ".mp4", ".mkv", ".avi", ".mov", ".webm",  # video
    ".mp3", ".wav", ".flac", ".m4a", ".ogg", ".aac",  # audio
}


def _validate_audio_path(audio_path: Path) -> Path:
    """Validate and canonicalize audio path for subprocess calls."""
    # Resolve to absolute path
    audio_path = audio_path.resolve()

    if not audio_path.exists():
        raise FileNotFoundError(f"File not found: {audio_path}")

    if not audio_path.is_file():
        raise ValueError(f"Path is not a file: {audio_path}")

    if audio_path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {audio_path.suffix}\n"
            f"Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    return audio_path


def check_ffmpeg() -> bool:
    """Check if ffmpeg is available in PATH."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def is_gpu_available(whisper_exe: str | Path | None = None) -> bool:
    """Check if whisper.cpp GPU backend is available."""
    exe_path = _resolve_path(whisper_exe, "WHISPER_CPP_EXE", _DEFAULT_WHISPER_EXE)
    return exe_path.exists()


class GpuTranscriber:
    """GPU-accelerated transcription using whisper.cpp with Intel SYCL."""

    VALID_MODELS = ["tiny", "base", "small", "medium", "large-v3", "turbo"]

    def __init__(
        self,
        model_size: str = "large-v3",
        whisper_exe: str | Path | None = None,
        models_dir: str | Path | None = None,
        oneapi_bin: str | None = None,
    ):
        if model_size not in self.VALID_MODELS:
            raise ValueError(f"Invalid model: {model_size}. Valid: {self.VALID_MODELS}")

        self.model_size = model_size
        self.whisper_exe = _resolve_path(whisper_exe, "WHISPER_CPP_EXE", _DEFAULT_WHISPER_EXE)
        self.models_dir = _resolve_path(models_dir, "WHISPER_CPP_MODELS", _DEFAULT_WHISPER_MODELS)
        self.oneapi_bin = _find_oneapi_bin(oneapi_bin)

        self.model_file = WHISPER_CPP_MODEL_MAP.get(model_size, "ggml-large-v3-turbo.bin")
        self.model_path = self.models_dir / self.model_file

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model not found: {self.model_path}\n"
                f"Download from: https://huggingface.co/ggerganov/whisper.cpp"
            )

    def _convert_to_wav(self, audio_path: Path) -> Path:
        """Convert audio/video to WAV format required by whisper.cpp."""
        # If already WAV with correct format, use directly
        if audio_path.suffix.lower() == ".wav":
            return audio_path

        # Create temp WAV file
        wav_path = Path(tempfile.gettempdir()) / f"{audio_path.stem}_whisper.wav"

        print(f"Converting to WAV format...")
        cmd = [
            "ffmpeg", "-y", "-i", str(audio_path),
            "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le",
            str(wav_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg conversion failed: {result.stderr}")

        return wav_path

    def _parse_timestamp(self, ts: str) -> float:
        """Parse timestamp like '00:01:23.456' to seconds."""
        parts = ts.split(":")
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = float(parts[2])
        return hours * 3600 + minutes * 60 + seconds

    def _parse_output(self, output: str) -> list[TranscriptSegment]:
        """Parse whisper.cpp output into segments."""
        segments = []
        # Pattern: [00:00:00.000 --> 00:00:07.620]   text here
        pattern = r'\[(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})\]\s*(.+)'

        for line in output.split("\n"):
            match = re.match(pattern, line)
            if match:
                start = self._parse_timestamp(match.group(1))
                end = self._parse_timestamp(match.group(2))
                text = match.group(3).strip()
                if text:
                    segments.append(TranscriptSegment(start=start, end=end, text=text))

        return segments

    def _is_transcript_line(self, line: str) -> bool:
        """Check if line is a transcript segment (starts with timestamp)."""
        return line.strip().startswith('[') and '-->' in line

    def transcribe(self, audio_path: str | Path, language: str = "en",
                   show_progress: bool = True, debug: bool = False) -> Iterator[TranscriptSegment]:
        """Transcribe using whisper.cpp GPU backend."""
        # Validate and canonicalize path
        audio_path = _validate_audio_path(Path(audio_path))

        # Pre-flight check: verify ffmpeg is available (needed for WAV conversion)
        if audio_path.suffix.lower() != ".wav" and not check_ffmpeg():
            raise RuntimeError(
                "ffmpeg not found in PATH. Please install ffmpeg:\n"
                "  Windows: winget install ffmpeg\n"
                "  Or download from: https://ffmpeg.org/download.html"
            )

        # Convert to WAV if needed
        wav_path = self._convert_to_wav(audio_path)
        temp_wav_created = wav_path != audio_path

        try:
            print(f"Transcribing with GPU (whisper.cpp): {audio_path.name}")
            print(f"Model: {self.model_file}")
            if show_progress:
                print("Streaming transcription...\n")
            else:
                print("Processing (output hidden)...\n")

            # Set environment for Intel GPU
            env = os.environ.copy()
            env["GGML_SYCL_DEVICE"] = "0"

            # Add Intel oneAPI bin to PATH for required DLLs (svml_dispmd.dll, etc.)
            if self.oneapi_bin:
                env["PATH"] = self.oneapi_bin + os.pathsep + env.get("PATH", "")

            cmd = [
                str(self.whisper_exe),
                "-m", str(self.model_path),
                "-f", str(wav_path),
                "-l", language or "en",
            ]

            # Stream output in real-time while capturing for parsing
            output_lines = []
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=env,
                bufsize=1
            )

            for line in process.stdout:
                output_lines.append(line)
                # Filter output based on flags
                if debug:
                    # Show everything
                    print(line, end='', flush=True)
                elif show_progress and self._is_transcript_line(line):
                    # Show only transcript lines
                    print(line, end='', flush=True)

            process.wait()

            if process.returncode != 0:
                raise RuntimeError(f"whisper.cpp failed with return code {process.returncode}")

            segments = self._parse_output(''.join(output_lines))
            for segment in segments:
                yield segment

        finally:
            # Clean up temp WAV file (guaranteed even on error)
            if temp_wav_created and wav_path.exists():
                wav_path.unlink()

    def transcribe_to_list(self, audio_path: str | Path, language: str = "en",
                           show_progress: bool = True, debug: bool = False) -> list[TranscriptSegment]:
        """Transcribe and return all segments as a list."""
        return list(self.transcribe(audio_path, language, show_progress, debug))


class Transcriber:
    """Wrapper for faster-whisper transcription with optimizations."""

    VALID_MODELS = ["tiny", "base", "small", "medium", "large-v3", "turbo"]

    def __init__(self, model_size: str = "large-v3", device: str = "cpu"):
        """
        Initialize the transcriber.

        Args:
            model_size: Model to use. Options: tiny, base, small, medium, large-v3, turbo
            device: Device to run on. Currently only "cpu" supported.
        """
        if model_size not in self.VALID_MODELS:
            raise ValueError(f"Invalid model: {model_size}. Valid: {self.VALID_MODELS}")

        self.model_size = model_size
        self.device = device
        self._model = None

    def _load_model(self):
        """Lazy-load the Whisper model."""
        if self._model is None:
            try:
                from faster_whisper import WhisperModel
            except ImportError:
                raise ImportError("faster-whisper not installed. Run: pip install faster-whisper")

            print(f"Loading {self.model_size} model (first run downloads ~1-3GB)...")
            self._model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type="int8"
            )
        return self._model

    def transcribe(self, audio_path: str | Path, language: str = None) -> Iterator[TranscriptSegment]:
        """
        Transcribe an audio/video file.

        Args:
            audio_path: Path to audio/video file
            language: Language code (e.g., "en"). Auto-detected if None.

        Yields:
            TranscriptSegment objects with timing and text
        """
        # Validate and canonicalize path
        audio_path = _validate_audio_path(Path(audio_path))

        model = self._load_model()

        print(f"Transcribing: {audio_path.name}")
        print("This may take a while for long recordings...\n")

        # Enable VAD filter to skip silence - major speed improvement
        segments, info = model.transcribe(
            str(audio_path),
            beam_size=5,
            language=language,
            vad_filter=True,
            vad_parameters={
                "min_silence_duration_ms": 500,  # Skip silence longer than 500ms
                "speech_pad_ms": 200,  # Padding around speech
            }
        )

        print(f"Detected language: {info.language} (probability: {info.language_probability:.2f})\n")

        for segment in segments:
            yield TranscriptSegment(
                start=segment.start,
                end=segment.end,
                text=segment.text.strip()
            )

    def transcribe_to_list(self, audio_path: str | Path, language: str = None) -> list[TranscriptSegment]:
        """Transcribe and return all segments as a list."""
        return list(self.transcribe(audio_path, language))


def format_time(seconds: float) -> str:
    """Convert seconds to HH:MM:SS format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"
