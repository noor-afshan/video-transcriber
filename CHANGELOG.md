# Changelog

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
