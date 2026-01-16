"""
Video Transcription Script with Speaker Diarization
Transcribes audio/video files locally with optional speaker identification.
Uses GPU acceleration (Intel Arc) by default for ~3x faster transcription.

Usage:
    python transcribe_video.py "path/to/recording.mp4"
    python transcribe_video.py "path/to/recording.mp4" --no-diarize
    python transcribe_video.py "path/to/recording.mp4" --model medium
    python transcribe_video.py "path/to/recording.mp4" --cpu
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


def _sanitize_filename(name: str) -> str:
    """Sanitize filename to prevent OS errors and path traversal."""
    # Remove/replace characters that are problematic on Windows
    # Reserved: < > : " / \ | ? *
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', name)
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    # Handle empty result
    return sanitized or "transcript"


def load_config(config_path: str = None) -> dict:
    """Load configuration from JSON file."""
    default_config = {
        "model": "large-v3",
        "huggingface_token": None,
        "min_speakers": 2,
        "max_speakers": 6,
        "cleanup": {
            "remove_duplicates": True,
            "remove_fillers": True,
            "remove_hallucinations": True,
            "remove_non_english": True,
            "min_segment_length": 3,
        }
    }

    if config_path and Path(config_path).exists():
        with open(config_path, "r") as f:
            user_config = json.load(f)
            # Merge with defaults
            for key, value in user_config.items():
                if isinstance(value, dict) and key in default_config:
                    default_config[key].update(value)
                else:
                    default_config[key] = value

    # Also check for config.json in script directory
    script_dir = Path(__file__).parent
    default_path = script_dir / "config.json"
    if not config_path and default_path.exists():
        with open(default_path, "r") as f:
            user_config = json.load(f)
            for key, value in user_config.items():
                if isinstance(value, dict) and key in default_config:
                    default_config[key].update(value)
                else:
                    default_config[key] = value

    return default_config


def transcribe_video(
    audio_path: str,
    model_size: str = "large-v3",
    enable_diarization: bool = True,
    enable_cleanup: bool = True,
    use_cpu: bool = False,
    show_progress: bool = True,
    debug: bool = False,
    config: dict = None,
) -> str:
    """
    Transcribe a video/audio recording with optional speaker diarization.

    Args:
        audio_path: Path to audio/video file
        model_size: Whisper model size
        enable_diarization: Whether to identify speakers
        enable_cleanup: Whether to clean hallucinations
        use_cpu: Force CPU backend (faster-whisper) instead of GPU
        show_progress: Show transcription progress in real-time
        debug: Show all whisper.cpp debug/initialization output
        config: Configuration dictionary

    Returns:
        Full transcript text
    """
    from modules.transcriber import Transcriber, GpuTranscriber, is_gpu_available, format_time
    from modules.cleaner import TranscriptCleaner

    config = config or {}
    audio_path = Path(audio_path)

    if not audio_path.exists():
        print(f"ERROR: File not found: {audio_path}")
        sys.exit(1)

    # Extract path configuration
    paths_config = config.get("paths", {})
    whisper_exe = paths_config.get("whisper_cpp_exe")
    models_dir = paths_config.get("whisper_cpp_models")
    oneapi_bin = paths_config.get("oneapi_bin")

    # Step 1: Transcribe (GPU default, fallback to CPU)
    if not use_cpu and is_gpu_available(whisper_exe):
        try:
            transcriber = GpuTranscriber(
                model_size=model_size,
                whisper_exe=whisper_exe,
                models_dir=models_dir,
                oneapi_bin=oneapi_bin,
            )
            transcript_segments = transcriber.transcribe_to_list(
                audio_path, show_progress=show_progress, debug=debug
            )
        except Exception as e:
            print(f"WARNING: GPU transcription failed: {e}")
            print("Falling back to CPU...\n")
            transcriber = Transcriber(model_size=model_size)
            transcript_segments = transcriber.transcribe_to_list(audio_path)
    else:
        if not use_cpu:
            print("GPU backend not found, using CPU (faster-whisper)...")
        transcriber = Transcriber(model_size=model_size)
        transcript_segments = transcriber.transcribe_to_list(audio_path)

    # Step 2: Diarize (if enabled)
    speaker_segments = None
    if enable_diarization:
        try:
            from modules.diarizer import Diarizer, assign_speakers_to_transcript

            hf_token = config.get("huggingface_token") or os.environ.get("HF_TOKEN")
            if not hf_token:
                print("\nWARNING: No HuggingFace token found. Skipping speaker diarization.")
                print("Set HF_TOKEN environment variable or add 'huggingface_token' to config.json")
                print("Get a token at: https://huggingface.co/settings/tokens\n")
                enable_diarization = False
            else:
                diarizer = Diarizer(
                    hf_token=hf_token,
                    min_speakers=config.get("min_speakers", 2),
                    max_speakers=config.get("max_speakers", 6),
                )
                speaker_segments = diarizer.diarize(audio_path)
        except Exception as e:
            print(f"\nWARNING: Diarization failed: {e}")
            print("Continuing without speaker identification.\n")
            enable_diarization = False

    # Step 3: Merge transcription with speakers
    from modules.diarizer import assign_speakers_to_transcript, segments_without_speakers

    if enable_diarization and speaker_segments:
        merged = assign_speakers_to_transcript(transcript_segments, speaker_segments)
    else:
        # No diarization - use "Speaker" for all
        merged = segments_without_speakers(transcript_segments)

    # Step 4: Clean up
    if enable_cleanup:
        cleanup_config = config.get("cleanup", {})
        cleaner = TranscriptCleaner(
            remove_duplicates=cleanup_config.get("remove_duplicates", True),
            remove_fillers=cleanup_config.get("remove_fillers", True),
            remove_hallucinations=cleanup_config.get("remove_hallucinations", True),
            remove_non_english=cleanup_config.get("remove_non_english", True),
            min_segment_length=cleanup_config.get("min_segment_length", 3),
        )
        merged = cleaner.clean(merged)

    # Step 5: Format and output
    print("=" * 60)
    print("TRANSCRIPT")
    print("=" * 60 + "\n")

    output_lines = []
    file_lines = []
    prev_speaker = None

    for seg in merged:
        timestamp = f"[{format_time(seg.start)} -> {format_time(seg.end)}]"
        line = f"{timestamp} {seg.speaker}: {seg.text}"
        print(line)
        output_lines.append(line)

        # For file output: group by speaker, add blank line on speaker change
        if prev_speaker and prev_speaker != seg.speaker:
            file_lines.append("")
        file_lines.append(f"{seg.speaker}: {seg.text}")
        prev_speaker = seg.speaker

    # Save to file (configurable output directory, defaults to input file's directory)
    output_dir = paths_config.get("output_dir")
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = audio_path.parent
    output_path = output_dir / (_sanitize_filename(audio_path.stem) + ".txt")
    output_path.write_text("\n".join(file_lines), encoding="utf-8")

    print("\n" + "=" * 60)
    print(f"Transcript saved to: {output_path}")
    print("=" * 60)

    return "\n".join(output_lines)


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe video/audio recordings with speaker identification (GPU accelerated)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python transcribe_video.py "video.mp4"              # GPU, large-v3, with speaker ID
  python transcribe_video.py "video.mp4" --no-diarize # Skip speaker identification
  python transcribe_video.py "video.mp4" -m medium    # Faster, slightly less accurate
  python transcribe_video.py "video.mp4" --cpu        # Force CPU (slower)

Models:
  tiny, base     Fast but less accurate
  small, medium  Good balance of speed/accuracy
  large-v3       Best accuracy (default)
  turbo          Same as large-v3 on GPU

Backend:
  GPU (default)  Intel Arc via whisper.cpp (~3x faster)
  CPU            faster-whisper (use --cpu flag)
        """
    )

    parser.add_argument("audio_file", help="Path to audio/video file")
    parser.add_argument(
        "--model", "-m",
        default=None,
        choices=["tiny", "base", "small", "medium", "large-v3", "turbo"],
        help="Whisper model size (default: large-v3)"
    )
    parser.add_argument(
        "--no-diarize",
        action="store_true",
        help="Disable speaker identification"
    )
    parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Keep raw transcript (no hallucination removal)"
    )
    parser.add_argument(
        "--cpu",
        action="store_true",
        help="Force CPU backend (faster-whisper) instead of GPU"
    )
    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Hide real-time transcription progress"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show all whisper.cpp initialization and debug output"
    )
    parser.add_argument(
        "--config", "-c",
        default=None,
        help="Path to config.json file"
    )

    args = parser.parse_args()

    # Load config
    config = load_config(args.config)

    # CLI args override config
    model = args.model or config.get("model", "large-v3")

    transcribe_video(
        audio_path=args.audio_file,
        model_size=model,
        enable_diarization=not args.no_diarize,
        enable_cleanup=not args.no_cleanup,
        use_cpu=args.cpu,
        show_progress=not args.no_progress,
        debug=args.debug,
        config=config,
    )


if __name__ == "__main__":
    main()
