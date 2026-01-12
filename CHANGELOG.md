# Changelog

## v1.1.0 - January 11, 2026

### Security

- **Safer file handling**: Temporary files now use unpredictable names (`mkstemp`) with guaranteed cleanup
- **Input validation**: Frame extraction validates fps parameter before passing to ffmpeg
- **API rate limiting**: Gemini API calls limited to 30 req/min to prevent quota exhaustion
- **Path validation**: All file paths validated before subprocess calls
- **Credential masking**: Sensitive tokens masked in `__repr__` methods

### Removed

- **OBS auto-recording**: Removed non-functional `auto_record.py` and related configuration
- **OBS WebSocket config**: Removed `obs` section from config.json (manual recording docs retained)

### Changed

- **Generalized terminology**: Renamed from "meeting" to "video" throughout codebase and docs
- **Better batch script**: Added file validation and PowerShell alternative (`transcribe.ps1`)

### Documentation

- Professional README with badges and quick start guide
- Six focused user guides in `docs/` folder
- GitHub issue and PR templates
- Archived legacy 544-line guide to `docs/_archive/`

---

## v1.0.0 - January 11, 2026

### Initial Release

A local video transcription tool with speaker identification - all processing happens on your device.

### Features

- **GPU-Accelerated Transcription**: Fast transcription using Intel Arc graphics via whisper.cpp
- **CPU Fallback**: Automatic fallback to faster-whisper when GPU unavailable
- **Speaker Diarization**: Identify and label different speakers in your videos
- **Hallucination Cleanup**: Automatic removal of common whisper artifacts and duplicates
- **Multiple Model Support**: Choose from tiny to large-v3 models based on speed/accuracy needs

### Utilities

- **Frame Extraction**: Extract key frames from videos
- **Frame Deduplication**: Remove duplicate/similar frames intelligently
- **Frame Classification**: Categorize extracted frames

### Output

- Clean timestamped transcripts with speaker labels
- Format: `[HH:MM:SS -> HH:MM:SS] Speaker 1: text`
- Automatic save to Videos folder

### Documentation

- Comprehensive user guide with OBS setup instructions
- CLI options reference
- Troubleshooting guide
