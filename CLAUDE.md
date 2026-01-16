# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

Local video transcription tool with speaker diarization. GPU-accelerated via Intel Arc (whisper.cpp) with fallback to CPU (faster-whisper). All processing happens on-device.

## Quick Commands

```bash
# Basic transcription (GPU, speaker ID on by default)
python transcribe_video.py "video.mp4"

# Skip speaker identification
python transcribe_video.py "video.mp4" --no-diarize

# Faster with medium model
python transcribe_video.py "video.mp4" --model medium

# Force CPU backend
python transcribe_video.py "video.mp4" --cpu
```

## Architecture

```
transcribe_video.py     # CLI entry point, orchestrates pipeline
modules/
├── transcriber.py        # GPU (whisper.cpp) and CPU (faster-whisper) backends
├── diarizer.py           # Speaker segmentation (pyannote-audio)
└── cleaner.py            # Hallucination/duplicate removal
config.json               # Settings (HF token, model, cleanup options)
```

## Dependencies

- **whisper.cpp**: GPU transcription via Intel SYCL (default)
- **faster-whisper**: CPU transcription fallback
- **pyannote.audio**: Speaker diarization (requires HuggingFace token)
- **torch**, **torchaudio**: ML framework
- **ffmpeg**: Audio conversion (required for GPU backend)

## Environment Variables

- `HF_TOKEN`: HuggingFace token for pyannote speaker diarization (required for default behavior)

## Default Behavior

| Option | Default |
|--------|---------|
| Backend | GPU (Intel Arc via whisper.cpp) |
| Model | `large-v3` |
| Speaker ID | **On** (use `--no-diarize` to disable) |
| Cleanup | On |

## Output

- **Console**: `[HH:MM:SS -> HH:MM:SS] Speaker 1: text`
- **File**: Saved to `C:\Users\piers\Videos\Captures\{filename}.txt`

## Development

```bash
# Activate virtual environment
.venv\Scripts\activate

# Type check (like C# build)
.venv\Scripts\pyright.exe .

# Lint check
.venv\Scripts\ruff.exe check .

# Run tests
.venv\Scripts\pytest.exe tests -v
```

## User Guide

See `docs/` folder for full usage documentation including OBS setup, CLI options, troubleshooting, and workflow.

## Claude Behavior Rules

- **Plan approval ≠ execution**: When a plan is approved, do NOT automatically start implementing. Wait for explicit instruction to proceed with implementation.
