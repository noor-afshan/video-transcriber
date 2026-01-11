# OBS Integration Guide

Set up OBS Studio for video capture with optional auto-recording.

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

## Auto-Recording

Automatically start/stop OBS recording based on window detection.

### Prerequisites

1. **Enable OBS WebSocket:**
   - OBS → Tools → WebSocket Server Settings
   - Check "Enable WebSocket Server"
   - Set a password
   - Default port: 4455

2. **Configure connection** in config.json:
   ```json
   {
     "obs": {
       "host": "localhost",
       "port": 4455
     }
   }
   ```

   Set password via environment variable:
   ```powershell
   setx OBS_PASSWORD "your_password"
   ```

### How It Works

The `auto_record.py` script:
- Runs silently in background
- Monitors for target windows (configurable)
- Starts OBS recording when window detected
- Stops recording when window closes

### Usage

```powershell
# Run with console output (for testing)
python auto_record.py

# Faster polling (check every 2 seconds)
python auto_record.py --poll-interval 2

# Auto-transcribe when recording ends
python auto_record.py --transcribe

# With transcription options
python auto_record.py --transcribe --model medium --no-diarize
```

### CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `--host` | OBS WebSocket host | From config |
| `--port` | OBS WebSocket port | From config |
| `--poll-interval` | Seconds between checks | 5 |
| `--transcribe` | Auto-transcribe when done | Off |
| `--no-diarize` | Skip speaker ID | Off |
| `--model` | Whisper model | large-v3 |
| `--cpu` | Force CPU backend | Off |

### Startup Automation

Run auto-record at Windows login:

1. Create a VBS script at:
   ```
   %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\AutoRecord.vbs
   ```

2. Contents:
   ```vbscript
   Set WshShell = CreateObject("WScript.Shell")
   WshShell.Run "pythonw ""C:\path\to\auto_record.py""", 0, False
   ```

### Disabling Auto-Record

Delete the startup entry:
```
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\AutoRecord.vbs
```

Or stop the running process via Task Manager (look for `pythonw.exe`).

## Troubleshooting

### Recording Not Starting

1. Ensure OBS is running before detection window appears
2. Check OBS WebSocket is enabled
3. Verify config.json matches OBS settings
4. Run manually to see errors: `python auto_record.py`

### Window Not Detected

1. Check window title matches detection pattern
2. Use faster polling: `--poll-interval 2`
3. Verify script is running in Task Manager

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
