# Transcription Guide

Complete reference for video transcription with Transcribe.

## Basic Usage

```powershell
# Basic transcription (GPU accelerated, speaker identification on)
python transcribe_video.py "video.mp4"

# Skip speaker identification (faster)
python transcribe_video.py "video.mp4" --no-diarize

# Use medium model (faster, slightly less accurate)
python transcribe_video.py "video.mp4" --model medium

# Force CPU backend
python transcribe_video.py "video.mp4" --cpu
```

## CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `--model, -m` | Model size | `large-v3` |
| `--no-diarize` | Disable speaker identification | Off (diarization on) |
| `--cpu` | Force CPU backend | Off (GPU preferred) |
| `--no-progress` | Hide real-time output | Off (progress shown) |
| `--debug` | Show GPU/initialization info | Off |
| `--no-cleanup` | Keep raw transcript | Off (cleanup on) |
| `--config FILE` | Custom config.json path | `config.json` |

## Model Selection

| Model | GPU Time (33 min audio) | Accuracy | Use Case |
|-------|-------------------------|----------|----------|
| `large-v3` | ~26 min | Best | Default - highest accuracy |
| `medium` | ~10-12 min | Very good | Good balance of speed/accuracy |
| `small` | ~5-6 min | Good | Faster processing |
| `base` | ~2-3 min | Basic | Quick drafts |
| `tiny` | ~1 min | Limited | Testing only |
| `turbo` | ~25 min (CPU) | Good | CPU-optimized model |

**Recommendation:** Start with `large-v3` (default). Use `medium` if you need faster results.

```powershell
# Best quality (default)
python transcribe_video.py "video.mp4"

# Faster with medium model
python transcribe_video.py "video.mp4" --model medium

# Quick draft
python transcribe_video.py "video.mp4" --model base --no-diarize
```

## Speaker Diarization

Speaker identification labels different voices as "Speaker 1", "Speaker 2", etc.

### Requirements

- HuggingFace token (free)
- Accepted pyannote model terms

See [Installation Guide](installation.md#huggingface-token-for-speaker-diarization) for setup.

### Configuration

Adjust expected speaker count in config.json:

```json
{
  "min_speakers": 2,
  "max_speakers": 6
}
```

### Disabling

```powershell
python transcribe_video.py "video.mp4" --no-diarize
```

## Output Format

### Console Output

```
[00:01:23 -> 00:01:35] Speaker 1: Good morning everyone, let's get started.
[00:01:36 -> 00:01:52] Speaker 2: Sure, I'll share my screen.
```

### File Output

Saved to your Videos folder as `{original_filename}.txt`:

```
Speaker 1: Good morning everyone, let's get started.

Speaker 2: Sure, I'll share my screen.
```

### Custom Output Location

Set in config.json:
```json
{
  "paths": {
    "output_dir": "D:\\Transcripts"
  }
}
```

## Hallucination Cleanup

Whisper sometimes produces artifacts like repeated phrases or non-English text. Cleanup is enabled by default.

### What Gets Removed

- Duplicate consecutive lines
- Common hallucinations ("Thank you for watching", "Subscribe", etc.)
- Non-English characters (configurable)
- Very short segments (< 3 characters)
- Filler sounds

### Configuration

```json
{
  "cleanup": {
    "remove_duplicates": true,
    "remove_fillers": true,
    "remove_hallucinations": true,
    "remove_non_english": true,
    "min_segment_length": 3
  }
}
```

### Disabling

```powershell
python transcribe_video.py "video.mp4" --no-cleanup
```

## Performance

### Backend Comparison

| Backend | Hardware | Speed | Setup |
|---------|----------|-------|-------|
| GPU (default) | Intel Arc | ~3x faster | Requires whisper.cpp + oneAPI |
| CPU | Any | Baseline | Works out of the box |

### Typical Times (33-minute audio)

| Configuration | Time |
|---------------|------|
| GPU + large-v3 | ~26 min |
| GPU + medium | ~10-12 min |
| GPU + small | ~5-6 min |
| CPU + large-v3 | ~45 min |
| CPU + turbo | ~25 min |
| + Speaker ID | Add ~10-15 min |

### Optimization Tips

1. **Skip speaker ID** if you don't need it: `--no-diarize`
2. **Use medium model** for faster results: `--model medium`
3. **Enable GPU** - it's ~3x faster than CPU
4. **Lower resolution recordings** process faster (audio quality matters more than video)

## Batch Processing

Process multiple files:

```powershell
# PowerShell - process all MP4s in folder
Get-ChildItem *.mp4 | ForEach-Object { python transcribe_video.py $_.FullName }

# With specific options
Get-ChildItem *.mp4 | ForEach-Object {
    python transcribe_video.py $_.FullName --model medium --no-diarize
}
```

## Windows Context Menu

Right-click any video file → "Transcribe"

To enable, run `transcribe-context-menu.reg` (see [Installation](installation.md#windows-context-menu-optional)).

---

[← Back to README](../README.md)
