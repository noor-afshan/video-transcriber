# Installation Guide

Complete setup instructions for Transcribe.

## System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| OS | Windows 10 | Windows 11 |
| Python | 3.10+ | 3.11+ |
| RAM | 8 GB | 16 GB |
| GPU | None (CPU fallback) | Intel Arc A770/A750 |

## Quick Install

```bash
git clone https://github.com/piersrobcoleman/video-transcriber.git
cd video-transcriber
pip install -r requirements.txt
```

## Dependencies

### Required

#### FFmpeg

FFmpeg is required for audio extraction from video files.

**Option 1: Winget (Recommended)**
```powershell
winget install ffmpeg
```

**Option 2: Chocolatey**
```powershell
choco install ffmpeg
```

**Option 3: Manual**
1. Download from https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to your PATH

**Verify installation:**
```powershell
ffmpeg -version
```

### Optional

#### HuggingFace Token (for Speaker Diarization)

Speaker identification requires a free HuggingFace token and access to the pyannote models.

1. **Create account**: https://huggingface.co/join
2. **Get token**: https://huggingface.co/settings/tokens
3. **Accept model terms**:
   - https://huggingface.co/pyannote/speaker-diarization-3.1
   - https://huggingface.co/pyannote/segmentation-3.0

4. **Set token** (choose one method):

   **Environment variable (recommended):**
   ```powershell
   setx HF_TOKEN "hf_your_token_here"
   ```
   Restart your terminal after setting.

   **Or in config.json:**
   ```json
   {
     "huggingface_token": "hf_your_token_here"
   }
   ```

Use `--no-diarize` flag to skip speaker identification if you don't have a token.

#### Gemini API Key (for Smart Frame Filtering)

AI-powered frame filtering removes non-content frames (talking heads, title cards).

1. **Get API key**: https://aistudio.google.com/apikey
2. **Set environment variable:**
   ```powershell
   setx GEMINI_API_KEY "your_key_here"
   ```

Use `--no-smart` flag to skip AI filtering if you don't have a key.

## GPU Setup (Intel Arc)

GPU acceleration provides ~3x faster transcription. If GPU is unavailable, the tool automatically falls back to CPU.

### Prerequisites

1. **Intel Arc GPU** (A770, A750, A580, or similar)
2. **Latest Intel GPU drivers**: https://www.intel.com/content/www/us/en/download/785597/intel-arc-iris-xe-graphics-windows.html

### whisper.cpp with SYCL

The tool uses whisper.cpp compiled with Intel SYCL support.

**Default location:**
```
C:\whisper.cpp\build_sycl\bin\whisper-cli.exe
```

**Custom location** - set in config.json:
```json
{
  "paths": {
    "whisper_cpp_exe": "D:\\path\\to\\whisper-cli.exe",
    "whisper_cpp_models": "D:\\path\\to\\models"
  }
}
```

### Intel oneAPI

The Intel oneAPI toolkit is required for SYCL support.

1. **Install oneAPI Base Toolkit**: https://www.intel.com/content/www/us/en/developer/tools/oneapi/base-toolkit-download.html
2. The tool auto-detects oneAPI versions in `C:\Program Files (x86)\Intel\oneAPI\*`

**Custom oneAPI location** - set in config.json:
```json
{
  "paths": {
    "oneapi_bin": "D:\\Intel\\oneAPI\\2025.0\\bin"
  }
}
```

### Verify GPU Setup

```powershell
python transcribe_video.py "test.mp4" --debug
```

Look for messages indicating Intel GPU detection. If GPU fails, the tool automatically falls back to CPU.

## Configuration

Copy the example configuration:

```powershell
cp config.json.example config.json
```

See [Configuration Reference](configuration.md) for all options.

## Verify Installation

```powershell
# Test transcription (CPU fallback is fine)
python transcribe_video.py "test.mp4" --no-diarize

# Test with speaker identification
python transcribe_video.py "test.mp4"

# Test frame extraction
python extract_frames.py "test.mp4" --no-smart
```

## Windows Context Menu (Optional)

Enable right-click transcription and frame extraction:

1. Run `transcribe-context-menu.reg` (adds "Transcribe" to video context menu)
2. Run `extract-frames-context-menu.reg` (adds "Extract Frames" to video context menu)

To remove, run the corresponding `-uninstall.reg` files.

## Troubleshooting

See [Troubleshooting Guide](troubleshooting.md) for common issues.

---

[← Back to README](../README.md)
