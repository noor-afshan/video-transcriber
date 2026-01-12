# Troubleshooting Guide

Common issues and solutions for Transcribe.

## Transcription Issues

### GPU Transcription Fails

**Symptoms:** Error messages about GPU/SYCL, or very slow transcription

**Solutions:**
1. The tool auto-falls back to CPU if GPU fails - this is normal
2. Use `--cpu` flag to force CPU backend
3. Check Intel GPU driver is up to date
4. Verify whisper.cpp location in config.json:
   ```json
   {
     "paths": {
       "whisper_cpp_exe": "C:\\whisper.cpp\\build_sycl\\bin\\whisper-cli.exe"
     }
   }
   ```
5. Run with `--debug` to see GPU initialization info

### Hallucinations in Transcript

**Symptoms:** Repeated phrases, non-English text, filler sounds

**Solutions:**
1. Cleanup is enabled by default
2. Check config.json cleanup settings:
   ```json
   {
     "cleanup": {
       "remove_duplicates": true,
       "remove_hallucinations": true,
       "remove_non_english": true
     }
   }
   ```
3. Use `--no-cleanup` to see raw output for debugging

### FFmpeg Not Found

**Symptoms:** Error about ffmpeg not being installed

**Solutions:**
1. Install FFmpeg:
   ```powershell
   winget install ffmpeg
   ```
2. Verify it's in PATH:
   ```powershell
   ffmpeg -version
   ```
3. Restart your terminal after installation

## Speaker Diarization Issues

### Diarization Not Working

**Symptoms:** No speaker labels, or error about HF_TOKEN

**Solutions:**
1. Ensure HF_TOKEN is set:
   ```powershell
   setx HF_TOKEN "hf_your_token_here"
   ```
2. **Restart your terminal** after setting the variable
3. Verify you accepted model terms:
   - https://huggingface.co/pyannote/speaker-diarization-3.1
   - https://huggingface.co/pyannote/segmentation-3.0
4. Use `--no-diarize` to skip speaker identification

### Wrong Speaker Count

**Symptoms:** Too many or too few speakers detected

**Solutions:**
Adjust speaker count hints in config.json:
```json
{
  "min_speakers": 2,
  "max_speakers": 6
}
```

## Frame Extraction Issues

### Smart Filtering Not Working

**Symptoms:** Error about API key, or frames not being filtered

**Solutions:**
1. Ensure `GEMINI_API_KEY` environment variable is set:
   ```powershell
   setx GEMINI_API_KEY "your_key_here"
   ```
2. Get a key from: https://aistudio.google.com/apikey
3. Restart your terminal after setting
4. Use `--no-smart` to skip AI filtering

### Too Many/Few Frames Kept

**Symptoms:** Deduplication keeping wrong frames

**Solutions:**
Adjust threshold (0-64, lower = stricter):
```powershell
# More strict (fewer duplicates detected)
python extract_frames.py video.mp4 --threshold 3

# More permissive (more duplicates detected)
python extract_frames.py video.mp4 --threshold 10
```

Default threshold is 5. If you see near-duplicate frames that only differ by speaker expression, try `--threshold 3`.

## Audio Issues

### Echo in Recording

**Possible causes:**
- **Test call:** Expected - Teams plays your voice back
- **Real call:** Check OBS Audio Mixer - you may be capturing mic twice

### Audio Not Recording

**Solutions:**
1. Check OBS Audio Mixer shows green/yellow bars when audio plays
2. Verify correct audio device selected in source properties
3. Use Audio Output Capture for system audio, Audio Input Capture for mic

### Video Window Not Captured

**Solutions:**
1. Use **Display Capture** instead of Window Capture
2. Video apps often open in separate windows that Window Capture misses

## Performance Issues

### Transcription Too Slow

**Solutions:**
1. Use a smaller model:
   ```powershell
   python transcribe_video.py video.mp4 --model medium
   ```
2. Skip speaker identification:
   ```powershell
   python transcribe_video.py video.mp4 --no-diarize
   ```
3. Ensure GPU is being used (check with `--debug`)

### Model Performance Reference

| Model | GPU Time (33 min) | Accuracy |
|-------|-------------------|----------|
| large-v3 | ~26 min | Best |
| medium | ~10-12 min | Very good |
| small | ~5-6 min | Good |
| base | ~2-3 min | Basic |

Speaker identification adds ~10-15 minutes.

## Getting Help

If your issue isn't listed here:

1. Run with `--debug` flag for more information
2. Check the [GitHub Issues](../../issues) for similar problems
3. [Open a new issue](../../issues/new?template=bug_report.md) with:
   - Command you ran
   - Full error message
   - Python version (`python --version`)
   - GPU model (if applicable)

---

[← Back to README](../README.md)
