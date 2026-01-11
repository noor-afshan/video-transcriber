# Video & Audio Capture Setup

Discreet Teams meeting recording for transcription and analysis. No visible bot or participant indicator.

---

## OBS Configuration

### Video Settings (Optimized for Transcription)
Settings → Video

| Setting | Value |
|---------|-------|
| Base (Canvas) Resolution | 2560x1600 (your monitor) |
| Output (Scaled) Resolution | **1280x800** |
| FPS | **5** |

### Output Settings
Settings → Output → Output Mode: **Advanced** → Recording tab

| Setting | Value |
|---------|-------|
| Type | Standard |
| Recording Path | `C:\Users\piers\Videos` |
| Recording Format | mp4 |
| Video Encoder | x264 |
| Rate Control | CRF |
| CRF | **28** |
| CPU Usage Preset | veryfast |
| Audio Encoder | FFmpeg AAC |

### Audio Settings
| Setting | Value |
|---------|-------|
| Audio Bitrate | 192 |

> **Note:** Audio quality matters for transcription - don't reduce audio bitrate.

### File Size Comparison

| Profile | ~Size per 30 min | Use Case |
|---------|------------------|----------|
| Optimized (current) | ~15-30 MB | Transcription + occasional frame review |
| High Quality | ~150-300 MB | Full visual analysis |

---

### High Quality Settings (Reference)

<details>
<summary>Click to expand original high-quality settings</summary>

Use these if you need full-resolution video for detailed visual analysis:

**Video Settings:**
| Setting | Value |
|---------|-------|
| Base (Canvas) Resolution | 2560x1600 |
| Output (Scaled) Resolution | 1920x1080 |
| FPS | 30 |

**Output Settings:**
| Setting | Value |
|---------|-------|
| CRF | 20 |

</details>

### Sources Setup

| Source Type | Name | Purpose |
|-------------|------|---------|
| **Display Capture** | Screen | Captures entire monitor |
| **Audio Output Capture** | Desktop Audio | Captures Teams audio (other participants) |
| **Audio Input Capture** | Mic/Aux | Captures your microphone |

> **Important:** Use Display Capture, NOT Window Capture. Teams opens calls in separate windows, and Window Capture only captures one specific window.

### Hotkeys
Settings → Hotkeys

Set shortcuts for:
- **Start Recording** (e.g., `Ctrl+Shift+R`)
- **Stop Recording** (e.g., `Ctrl+Shift+S`)

---

## Recording Workflow

### Manual Recording
1. **Before meeting** → Open OBS, minimize it
2. **Meeting starts** → Press hotkey or click Start Recording
3. **Meeting ends** → Press hotkey or click Stop Recording
4. **Find recording** → `C:\Users\piers\Videos\[timestamp].mp4`

### Auto-Record (Recommended)

Automatically starts/stops OBS recording when Teams meetings begin/end.

#### Prerequisites

1. **Enable OBS WebSocket:**
   - OBS → Tools → WebSocket Server Settings
   - Check "Enable WebSocket Server"
   - Set password (configured in `config.json`)
   - Default port: 4455

2. **Config:** Password is stored in `config.json`:
   ```json
   "obs": {
     "host": "localhost",
     "port": 4455,
     "password": "your_password"
   }
   ```

#### How It Works

The `auto_record.py` script:
- Runs silently in background at Windows startup
- Monitors for Teams meeting windows
- Starts OBS recording when meeting detected
- Stops recording when meeting ends

#### Startup Setup

Already configured to run at login via:
```
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\TeamsAutoRecord.vbs
```

#### Manual Usage

```powershell
# Run with console output (for testing/debugging)
python auto_record.py

# Faster polling (check every 2 seconds instead of 5)
python auto_record.py --poll-interval 2

# Auto-transcribe when meeting ends
python auto_record.py --transcribe

# With transcription options
python auto_record.py --transcribe --model medium --no-diarize
```

#### CLI Options

| Option | Description |
|--------|-------------|
| `--host` | OBS WebSocket host (default: from config) |
| `--port` | OBS WebSocket port (default: from config) |
| `--password` | OBS WebSocket password (default: from config) |
| `--poll-interval` | Seconds between checks (default: 5) |
| `--transcribe` | Auto-transcribe when recording stops |
| `--no-diarize` | Skip speaker ID in transcription |
| `--model` | Whisper model for transcription |
| `--cpu` | Use CPU backend for transcription |

#### Disabling Auto-Record

Delete the startup entry:
```
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\TeamsAutoRecord.vbs
```

---

## Transcription

### Script Location
```
C:\Users\piers\OneDrive\Projects\Transcribe\transcribe_meeting.py
```

### Features
- **GPU acceleration** - Intel Arc via whisper.cpp (~3x faster than CPU)
- **Speaker diarization** - Identifies different speakers (Speaker 1, Speaker 2, etc.) - ON by default
- **Hallucination cleanup** - Removes repeated lines, non-English artifacts, filler words
- **Auto fallback** - Falls back to CPU (faster-whisper) if GPU unavailable

### Basic Usage
```powershell
# Basic transcription (GPU accelerated, with speaker identification)
python "C:\Users\piers\OneDrive\Projects\Transcribe\transcribe_meeting.py" "C:\Users\piers\Videos\recording.mp4"

# Skip speaker identification (faster)
python "C:\Users\piers\OneDrive\Projects\Transcribe\transcribe_meeting.py" "recording.mp4" --no-diarize

# Faster with medium model
python "C:\Users\piers\OneDrive\Projects\Transcribe\transcribe_meeting.py" "recording.mp4" --model medium

# Force CPU backend (if GPU issues)
python "C:\Users\piers\OneDrive\Projects\Transcribe\transcribe_meeting.py" "recording.mp4" --cpu

# Drag-and-drop via batch file
C:\Users\piers\OneDrive\Projects\Transcribe\transcribe.bat "recording.mp4"
```

### Default Behavior

Running `python transcribe_meeting.py "recording.mp4"` with no flags:

| Setting | Default | Notes |
|---------|---------|-------|
| Backend | **GPU** | Intel Arc via whisper.cpp (~3x faster) |
| Model | `large-v3` | Best accuracy |
| Speaker ID | **On** | Use `--no-diarize` to disable (requires HF_TOKEN) |
| Cleanup | On | Removes hallucinations, duplicates, fillers |
| Progress | **On** | Shows transcription in real-time |
| Debug | Off | Use `--debug` to show GPU/init info |

### CLI Options

| Option | Description |
|--------|-------------|
| `--model, -m` | Model size: tiny, base, small, medium, large-v3 (default), turbo |
| `--no-diarize` | Disable speaker identification |
| `--cpu` | Force CPU backend (faster-whisper) instead of GPU |
| `--no-progress` | Hide real-time transcription output |
| `--debug` | Show all whisper.cpp initialization and GPU info |
| `--no-cleanup` | Keep raw transcript without hallucination removal |
| `--config FILE` | Custom config.json path |

### Model Options

| Model | GPU Time (33 min audio) | Accuracy | Use Case |
|-------|-------------------------|----------|----------|
| `large-v3` | ~26 min | Best | Default - highest accuracy |
| `medium` | ~10-12 min | Very good | Good balance |
| `small` | ~5-6 min | Good | Faster processing |
| `base` | ~2-3 min | Basic | Quick drafts |

```powershell
# Best quality (default)
python transcribe_meeting.py "recording.mp4"

# Faster with medium model
python transcribe_meeting.py "recording.mp4" --model medium

# Skip speaker ID for speed
python transcribe_meeting.py "recording.mp4" --no-diarize
```

### Output Format

**Console output:**
```
[00:01:23 -> 00:01:35] Speaker 1: Good morning everyone, let's get started.
[00:01:36 -> 00:01:52] Speaker 2: Sure, I'll share my screen.
```

**File output (.txt):**
```
Speaker 1: Good morning everyone, let's get started.

Speaker 2: Sure, I'll share my screen.
```

### Speaker Diarization Setup (Required)

Speaker identification is enabled by default and requires a free HuggingFace token:

1. **Get token**: https://huggingface.co/settings/tokens
2. **Accept model terms**: https://huggingface.co/pyannote/speaker-diarization-3.1
3. **Set token**:
   ```powershell
   # Environment variable (recommended)
   setx HF_TOKEN "hf_your_token_here"
   ```
   Then restart your terminal.

Use `--no-diarize` to skip speaker identification if you don't have a token.

### Performance

| Backend | Model | ~Time for 33-min audio |
|---------|-------|------------------------|
| **GPU (default)** | large-v3 | ~26 min |
| **GPU** | medium | ~10-12 min |
| **GPU** | small | ~5-6 min |
| CPU (`--cpu`) | large-v3 | ~45 min |
| CPU (`--cpu`) | turbo | ~25 min |
| Speaker ID | any | Add ~10-15 min |

---

## Video Analysis (Screen Shares)

### Extract Frames (Recommended)

**Right-click method:** Right-click any video file → "Extract Frames"
- Extracts at 1 fps with deduplication and AI smart filtering (all on by default)
- Dedupe runs first (fast, local) to reduce frame count dramatically
- Smart filter then removes non-content frames (talking heads, title cards, ads) from the smaller set
- Requires running `extract-frames-context-menu.reg` once to enable
- Requires `GEMINI_API_KEY` or `GOOGLE_API_KEY` environment variable for smart filtering

**Command line:**
```powershell
# Full processing: Extract → Dedupe → Smart filter (default)
python extract_frames.py "recording.mp4"

# Skip AI filtering (dedupe only)
python extract_frames.py "recording.mp4" --no-smart

# Skip deduplication (smart filter only)
python extract_frames.py "recording.mp4" --no-dedupe

# Raw extraction only (no filtering or deduplication)
python extract_frames.py "recording.mp4" --no-smart --no-dedupe

# Custom frame rate (1 frame every 5 seconds)
python extract_frames.py "recording.mp4" --fps 1/5

# Custom output directory
python extract_frames.py "recording.mp4" --output my_frames
```

### Example Output

```
Extracting frames from: meeting-recording.mp4
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

### Frame Extraction Options

| Option | Default | Description |
|--------|---------|-------------|
| `--smart, -s` | **On** | AI filter: remove non-content frames (use `--no-smart` to disable) |
| `--dedupe, -d` | **On** | Remove duplicate frames (use `--no-dedupe` to disable) |
| `--fps, -f` | `1` | Frame rate: `1`, `1/2`, `1/5`, `1/10` |
| `--threshold, -t` | `5` | Deduplication sensitivity 0-64 |
| `--output, -o` | `frames/` | Output directory (default: next to video) |

### Frame Rate Guide

| Interval | Frames for 30-min meeting | Best for                   |
|----------|---------------------------|----------------------------|
| fps=1    | 1,800 frames              | Fast slide flipping, demos |
| fps=1/2  | 900 frames                | Typical presentations      |
| fps=1/5  | 360 frames                | Slow-paced slides          |
| fps=1/10 | 180 frames                | Very slow-paced content    |

### Smart Filtering

The `--smart` flag (on by default) uses Gemini AI to identify and remove non-content frames.

**What gets kept:**
- Active screen content: code, UI, documents, applications, websites
- Diagrams, charts, technical information
- Any of the above with a small person overlay (PiP)

**What gets removed:**
- Full-screen talking head (person only, no screen content)
- Title cards and large text overlays (e.g., "What Changed", "Coming Up Next")
- Transition slides, intro/outro frames
- Full-screen social media posts or tweets
- Sponsorship segments, ads, "link in description" callouts

### Duplicate Frame Removal

Meetings often have static screens (same slide for minutes). The `--dedupe` flag (on by default) uses perceptual hashing to detect and remove visually identical frames.

**Typical results:** 80-90% reduction in frame count (e.g., 156 frames -> 22 unique frames)

**Standalone tool** (for existing frame folders):
```powershell
# Dedupe + smart filter (default)
python dedupe_frames.py frames/

# Skip AI filtering
python dedupe_frames.py frames/ --no-smart

# Preview what would be deleted
python dedupe_frames.py frames/ --dry-run

# More strict (fewer duplicates detected)
python dedupe_frames.py frames/ --threshold 3

# More permissive (more duplicates detected)
python dedupe_frames.py frames/ --threshold 10
```

> **Tip:** If you see near-duplicate frames that only differ by speaker expression (mouth open/closed), try `--threshold 3` for stricter matching.

### Analysis Options

| Method | Use Case |
|--------|----------|
| Send frames to Claude | Diagrams, architecture, code on screen |
| Tesseract OCR | Bulk text extraction |
| Azure Video Indexer | Automated indexing, scene detection |

---

## Testing

### Teams Solo Meeting
1. Calendar → **Meet now** → Start meeting
2. Join alone, share screen, talk
3. Record with OBS
4. Leave meeting and check recording

### Teams Test Call
Settings → Devices → **Make a test call**

> Note: Test call plays your voice back, causing expected echo. Real meetings won't have this.

---

## Troubleshooting

### Echo in Recording
- **Test call:** Expected - it plays your voice back
- **Real meeting:** Check Audio Mixer - you may be capturing mic twice

### Audio Not Recording
- Check Audio Mixer shows green/yellow bars when audio plays
- Verify correct audio device selected in source properties

### Teams Window Not Captured
- Use **Display Capture** instead of Window Capture
- Teams opens calls in separate windows

### Diarization Not Working
- Ensure HF_TOKEN is set (restart terminal after `setx`)
- Verify you accepted model terms on HuggingFace
- Use `--no-diarize` to skip if token issues

### GPU Transcription Fails
- Script auto-falls back to CPU if GPU fails
- Use `--cpu` to force CPU backend
- Check Intel GPU driver is up to date
- whisper.cpp location: `C:\Users\piers\OneDrive\Projects\whisper.cpp\build_sycl\bin\whisper-cli.exe`

### Hallucinations in Transcript
- Cleanup is enabled by default
- If still seeing issues, check config.json cleanup settings
- Use `--no-cleanup` to see raw output for debugging

### Auto-Record Not Starting
- Ensure OBS is running before the meeting starts
- Check OBS WebSocket is enabled: Tools → WebSocket Server Settings
- Verify password in `config.json` matches OBS WebSocket password
- Run `python auto_record.py` manually to see error messages

### Auto-Record Not Detecting Meeting
- Teams meeting window must contain "Meeting with" or "| Microsoft Teams"
- Run `python auto_record.py --poll-interval 2` for faster detection
- Check Task Manager for `pythonw.exe` to verify script is running

### Smart Filtering Not Working
- Ensure `GEMINI_API_KEY` or `GOOGLE_API_KEY` environment variable is set
- Get a key from Google AI Studio: https://aistudio.google.com/apikey
- Set it: `setx GEMINI_API_KEY "your_key_here"` (then restart terminal)
- Use `--no-smart` to skip AI filtering if you don't have an API key

---

## Quick Reference

```powershell
# Basic transcription (GPU accelerated, with speaker ID)
python transcribe_meeting.py "recording.mp4"

# Faster with medium model
python transcribe_meeting.py "recording.mp4" -m medium

# Skip speaker identification
python transcribe_meeting.py "recording.mp4" --no-diarize

# Force CPU backend
python transcribe_meeting.py "recording.mp4" --cpu

# Extract frames (smart filter + dedupe on by default)
python extract_frames.py "recording.mp4"

# Extract frames without AI filtering
python extract_frames.py "recording.mp4" --no-smart

# Extract frames at lower rate
python extract_frames.py "recording.mp4" --fps 1/5

# Process existing frames folder (smart filter + dedupe)
python dedupe_frames.py frames/
```

---

## Analysis Workflow

1. **Record** meeting with OBS
2. **Transcribe** - right-click video → "Transcribe" (speakers identified automatically)
3. **Extract frames** - right-click video → "Extract Frames" (auto smart-filters + dedupes)
4. **Send to Claude** for:
   - Requirements elicitation
   - Action items extraction (grouped by speaker)
   - Implementation recommendations
   - Architecture analysis

---

## What Claude Can Do With Your Transcript

Once you paste a meeting transcript, Claude can:

**Requirements Elicitation:**
- Extract functional/non-functional requirements
- Identify user stories and acceptance criteria
- Flag ambiguous or conflicting requirements
- Create a requirements traceability matrix

**Implementation Recommendations:**
- Suggest architecture patterns
- Recommend tech stack based on requirements
- Break down into epics/features/tasks
- Identify risks and dependencies
- Provide code scaffolding or examples

**Other Analysis:**
- Summarize key decisions made
- List action items by person/speaker
- Identify open questions needing follow-up
- Create meeting minutes
