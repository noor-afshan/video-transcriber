# OBS Integration Guide

Set up OBS Studio for video capture.

## OBS Configuration

### Video Settings

Settings → Video

| Setting | Value | Notes |
|---------|-------|-------|
| Base (Canvas) Resolution | Your monitor resolution | e.g., 2560x1600 |
| Output (Scaled) Resolution | **1280x800** | Lower for smaller files |
| FPS | **5** | Sufficient for transcription |

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
| Audio Bitrate | 192 |

> **Note:** Audio quality matters for transcription - don't reduce audio bitrate below 128.

### File Size Comparison

| Profile | ~Size per 30 min | Use Case |
|---------|------------------|----------|
| Optimized (above) | ~15-30 MB | Transcription + occasional frame review |
| High Quality | ~150-300 MB | Full visual analysis |

<details>
<summary>High Quality Settings (Reference)</summary>

Use these if you need full-resolution video for detailed visual analysis:

**Video Settings:**
| Setting | Value |
|---------|-------|
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
| **Audio Output Capture** | Desktop Audio | Captures system audio |
| **Audio Input Capture** | Mic/Aux | Captures your microphone |

> **Important:** Use Display Capture, NOT Window Capture. Video apps often open in separate windows that Window Capture misses.

### Hotkeys

Settings → Hotkeys

Set shortcuts for:
- **Start Recording** (e.g., `Ctrl+Shift+R`)
- **Stop Recording** (e.g., `Ctrl+Shift+S`)

## Manual Recording

1. **Before video** → Open OBS, minimize it
2. **Video starts** → Press hotkey or click Start Recording
3. **Video ends** → Press hotkey or click Stop Recording
4. **Find recording** → `C:\Users\piers\Videos\[timestamp].mp4`

## Troubleshooting

### Audio Issues

| Issue | Solution |
|-------|----------|
| Echo | Check Audio Mixer - may be capturing mic twice |
| No audio | Verify Audio Mixer shows green/yellow bars |
| Wrong audio | Check source properties for correct device |

### Window Not Captured

Use **Display Capture** instead of Window Capture - video apps often use separate windows.

---

[← Back to README](../README.md)
