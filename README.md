<div align="center">

# Transcribe

**Local-first video transcription with GPU acceleration, speaker diarization, and AI-powered frame extraction**

![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Platform Windows](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows&logoColor=white)
![License MIT](https://img.shields.io/badge/License-MIT-green)
![GPU Intel Arc](https://img.shields.io/badge/GPU-Intel%20Arc-0071C5?logo=intel&logoColor=white)

</div>

---

## Features

- **GPU-Accelerated Transcription** - Fast transcription using Intel Arc graphics via whisper.cpp (~3x faster than CPU)
- **CPU Fallback** - Automatic fallback to faster-whisper when GPU unavailable
- **Speaker Diarization** - Identify and label different speakers (Speaker 1, Speaker 2, etc.)
- **Hallucination Cleanup** - Automatic removal of common Whisper artifacts and duplicates
- **Frame Extraction** - Extract key frames from videos with perceptual hash deduplication
- **AI Smart Filtering** - Remove non-content frames (talking heads, title cards) using Gemini API
- **OBS Integration** - Manual recording workflow for capturing video content
- **Windows Context Menu** - Right-click any video to transcribe or extract frames

## Quick Start

### 1. Install Dependencies

```bash
git clone https://github.com/piersrobcoleman/video-transcriber.git
cd video-transcriber
pip install -r requirements.txt
```

### 2. Configure (Optional)

Copy the example config and add your HuggingFace token for speaker diarization:

```bash
cp config.json.example config.json
# Edit config.json and add your huggingface_token
```

Or set the environment variable:
```powershell
setx HF_TOKEN "hf_your_token_here"
```

### 3. Transcribe

```bash
# Basic transcription (GPU accelerated, speaker identification on)
python transcribe_video.py "video.mp4"

# Skip speaker identification (faster)
python transcribe_video.py "video.mp4" --no-diarize

# Use medium model for faster processing
python transcribe_video.py "video.mp4" --model medium

# Force CPU backend
python transcribe_video.py "video.mp4" --cpu
```

## Output

**Console:**
```
[00:01:23 -> 00:01:35] Speaker 1: Welcome to today's presentation on cloud architecture.
[00:01:36 -> 00:01:52] Speaker 2: Let's start with the system overview diagram.
```

**File:** Saved to `Videos/` folder as `{filename}.txt`

## Documentation

| Guide | Description |
|-------|-------------|
| [Installation](docs/installation.md) | Full setup including GPU drivers and dependencies |
| [Transcription](docs/transcription.md) | CLI options, model selection, performance tips |
| [Frame Extraction](docs/frame-extraction.md) | Extract and filter frames with AI |
| [OBS Integration](docs/obs-integration.md) | Recording setup for video capture |
| [Configuration](docs/configuration.md) | Complete config.json reference |
| [Troubleshooting](docs/troubleshooting.md) | Common issues and solutions |

## Privacy

All transcription happens **locally on your device**. Audio never leaves your machine.

Frame classification (optional `--smart` flag) uses the Gemini API - images are sent to Google's servers for analysis. Use `--no-smart` to keep everything local.

## Requirements

- Windows 10/11
- Python 3.10+
- FFmpeg (for audio conversion)
- Intel Arc GPU (optional, for acceleration)
- HuggingFace token (optional, for speaker diarization)

## License

[MIT](LICENSE)

---

<div align="center">

**[Report Bug](../../issues/new?template=bug_report.md)** · **[Request Feature](../../issues/new?template=feature_request.md)** · **[Roadmap](ROADMAP.md)**

</div>
