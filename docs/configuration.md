# Configuration Reference

Complete reference for `config.json` options.

## Quick Start

```powershell
cp config.json.example config.json
```

Edit `config.json` with your settings. All fields are optional - sensible defaults are used.

## Full Configuration

```json
{
  "model": "large-v3",
  "huggingface_token": null,
  "paths": {
    "whisper_cpp_exe": null,
    "whisper_cpp_models": null,
    "output_dir": null,
    "oneapi_bin": null
  },
  "obs": {
    "host": "localhost",
    "port": 4455
  },
  "min_speakers": 2,
  "max_speakers": 6,
  "cleanup": {
    "remove_duplicates": true,
    "remove_fillers": true,
    "remove_hallucinations": true,
    "remove_non_english": true,
    "min_segment_length": 3
  }
}
```

## Options Reference

### General

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `model` | string | `"large-v3"` | Default Whisper model |
| `huggingface_token` | string | `null` | HuggingFace token for speaker diarization |

### Paths

Configure custom paths for tools and output.

| Option | Default | Description |
|--------|---------|-------------|
| `whisper_cpp_exe` | Auto-detect | Path to whisper-cli.exe |
| `whisper_cpp_models` | Auto-detect | Directory containing GGML models |
| `output_dir` | Videos folder | Where transcripts are saved |
| `oneapi_bin` | Auto-detect | Intel oneAPI bin directory |

**Defaults:**
- `whisper_cpp_exe`: `C:\whisper.cpp\build_sycl\bin\whisper-cli.exe`
- `whisper_cpp_models`: `C:\whisper.cpp\models`
- `output_dir`: User's Videos folder
- `oneapi_bin`: Auto-detected from `C:\Program Files (x86)\Intel\oneAPI\*`

**Example custom paths:**
```json
{
  "paths": {
    "whisper_cpp_exe": "D:\\Tools\\whisper-cli.exe",
    "whisper_cpp_models": "D:\\Models\\whisper",
    "output_dir": "D:\\Transcripts",
    "oneapi_bin": "C:\\Program Files (x86)\\Intel\\oneAPI\\2025.0\\bin"
  }
}
```

### OBS Integration

| Option | Default | Description |
|--------|---------|-------------|
| `host` | `"localhost"` | OBS WebSocket host |
| `port` | `4455` | OBS WebSocket port |

**Note:** OBS password should be set via environment variable for security:
```powershell
setx OBS_PASSWORD "your_password"
```

### Speaker Diarization

| Option | Default | Description |
|--------|---------|-------------|
| `min_speakers` | `2` | Minimum expected speakers |
| `max_speakers` | `6` | Maximum expected speakers |

These hints help the diarization model. Adjust based on your typical videos:
- One-on-one: `"min_speakers": 2, "max_speakers": 2`
- Panel discussion: `"min_speakers": 3, "max_speakers": 8`

### Transcript Cleanup

| Option | Default | Description |
|--------|---------|-------------|
| `remove_duplicates` | `true` | Remove repeated consecutive lines |
| `remove_fillers` | `true` | Remove filler sounds (um, uh, etc.) |
| `remove_hallucinations` | `true` | Remove common Whisper artifacts |
| `remove_non_english` | `true` | Remove non-English characters |
| `min_segment_length` | `3` | Minimum characters for a segment |

**Disable all cleanup:**
```json
{
  "cleanup": {
    "remove_duplicates": false,
    "remove_fillers": false,
    "remove_hallucinations": false,
    "remove_non_english": false,
    "min_segment_length": 0
  }
}
```

Or use the `--no-cleanup` flag.

## Environment Variables

Some settings can be overridden via environment variables:

| Variable | Purpose |
|----------|---------|
| `HF_TOKEN` | HuggingFace token (overrides config) |
| `OBS_PASSWORD` | OBS WebSocket password |
| `GEMINI_API_KEY` | Gemini API key for smart filtering |
| `GOOGLE_API_KEY` | Alternative to GEMINI_API_KEY |

Environment variables take precedence over config.json values.

## Config File Location

The tool looks for `config.json` in:
1. Path specified by `--config` flag
2. Current working directory
3. Same directory as the script

---

[← Back to README](../README.md)
