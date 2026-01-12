# Frame Extraction Guide

Extract and filter key frames from videos for analysis.

## Overview

The frame extraction pipeline:

1. **Extract** - Pull frames at specified interval (default: 1 fps)
2. **Deduplicate** - Remove visually identical frames using perceptual hashing
3. **Smart Filter** - Remove non-content frames using AI (optional)

Typical result: **80-90% reduction** in frame count.

## Basic Usage

```powershell
# Full pipeline: extract → dedupe → smart filter
python extract_frames.py "video.mp4"

# Skip AI filtering (dedupe only)
python extract_frames.py "video.mp4" --no-smart

# Skip deduplication (extract + smart filter)
python extract_frames.py "video.mp4" --no-dedupe

# Raw extraction only
python extract_frames.py "video.mp4" --no-smart --no-dedupe
```

## CLI Options

| Option | Default | Description |
|--------|---------|-------------|
| `--smart, -s` | **On** | AI filter: remove non-content frames |
| `--dedupe, -d` | **On** | Remove duplicate frames |
| `--fps, -f` | `1` | Frame rate (frames per second) |
| `--threshold, -t` | `5` | Deduplication sensitivity (0-64) |
| `--output, -o` | Next to video | Output directory |
| `--no-smart` | - | Disable AI filtering |
| `--no-dedupe` | - | Disable deduplication |

## Frame Rate Selection

| Interval | Frames/30 min | Best For |
|----------|---------------|----------|
| `--fps 1` | 1,800 | Fast slide flipping, demos |
| `--fps 1/2` | 900 | Typical presentations |
| `--fps 1/5` | 360 | Slow-paced slides |
| `--fps 1/10` | 180 | Very slow content |

```powershell
# Extract 1 frame every 5 seconds
python extract_frames.py "video.mp4" --fps 1/5
```

## Deduplication

Videos often have static screens (same slide for minutes). Deduplication uses perceptual hashing to detect and remove visually identical frames.

### How It Works

1. Computes perceptual hash for each frame
2. Compares adjacent frames
3. Removes frames within threshold similarity

### Threshold Tuning

Lower threshold = stricter matching (fewer frames removed)
Higher threshold = looser matching (more frames removed)

```powershell
# Default (threshold 5)
python extract_frames.py "video.mp4"

# Stricter - keeps more frames, removes only exact duplicates
python extract_frames.py "video.mp4" --threshold 3

# Looser - removes more similar frames
python extract_frames.py "video.mp4" --threshold 10
```

**Tip:** If you see near-duplicate frames that differ only by speaker expression (mouth open/closed), use `--threshold 3`.

## Smart Filtering (AI)

Uses Gemini API to classify frames and remove non-content.

### Requirements

1. **Gemini API key**: https://aistudio.google.com/apikey
2. Set environment variable:
   ```powershell
   setx GEMINI_API_KEY "your_key_here"
   ```

### What Gets Kept

- Active screen content: code, UI, documents, applications
- Diagrams, charts, technical information
- Content with small person overlay (picture-in-picture)

### What Gets Removed

- Full-screen talking head (person only, no content)
- Title cards and large text overlays
- Transition slides, intro/outro frames
- Social media posts, tweets
- Sponsorship segments, ads

### Privacy Note

When using `--smart`, images are sent to Google's Gemini API for analysis. Use `--no-smart` to keep everything local.

## Standalone Deduplication

Process an existing folder of frames:

```powershell
# Dedupe + smart filter
python dedupe_frames.py frames/

# Skip AI filtering
python dedupe_frames.py frames/ --no-smart

# Preview what would be deleted
python dedupe_frames.py frames/ --dry-run
```

## Example Output

```
Extracting frames from: recording.mp4
Output directory: C:\Users\piers\Videos\frames
Frame rate: 1 fps

[Pass 1/3] Extracting frames (ffmpeg)
Extracted 1038 frames [12.4s]

[Pass 2/3] Removing visually identical frames (perceptual hashing)
1038 -> 199 frames (839 duplicates removed) [2.1s]

[Pass 3/3] Filtering non-content frames
Using Gemini 2.0 Flash AI via API...
  [1/199] frame_0001.png: person
  [2/199] frame_0002.png: content
  ...
199 -> 149 frames (50 non-content frames removed) [45.3s]

Complete: 1038 -> 149 frames (86% reduction) [59.8s total]
```

## Analysis Workflow

1. **Extract frames** from video
2. **Send to Claude** for analysis:
   - Architecture diagrams
   - Code on screen
   - UI mockups
   - Technical documentation

```powershell
# Extract frames
python extract_frames.py "recording.mp4"

# Frames saved to recording_frames/
# Upload to Claude for analysis
```

## Windows Context Menu

Right-click any video → "Extract Frames"

To enable, run `extract-frames-context-menu.reg` (see [Installation](installation.md#windows-context-menu-optional)).

## Troubleshooting

### Smart Filter Not Working

- Check `GEMINI_API_KEY` is set
- Restart terminal after setting environment variable
- Use `--no-smart` to skip AI filtering

### Too Many Frames Kept

- Lower the threshold: `--threshold 3`
- Reduce frame rate: `--fps 1/5`

### Too Few Frames Kept

- Raise the threshold: `--threshold 10`
- Disable smart filtering: `--no-smart`

---

[← Back to README](../README.md)
