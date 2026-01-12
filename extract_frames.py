#!/usr/bin/env python3
"""Extract frames from video files using ffmpeg."""

import argparse
import re
import subprocess
import sys
import time
from pathlib import Path

from modules.deduplicator import FrameDeduplicator
from modules.frame_classifier import FrameClassifier


def _validate_fps(fps: str) -> str:
    """
    Validate fps parameter format.

    Args:
        fps: Frame rate string (e.g., "1", "0.5", "1/2", "1/30")

    Returns:
        The validated fps string.

    Raises:
        ValueError: If fps format is invalid.
    """
    # Allow formats: "1", "30", "0.5", "1.5", "1/2", "1/30"
    if not re.match(r'^(\d+(\.\d+)?|\d+/\d+)$', fps):
        raise ValueError(
            f"Invalid fps format: '{fps}'. "
            f"Use integer ('1'), decimal ('0.5'), or fraction ('1/2') format."
        )

    # Check for division by zero in fractions
    if '/' in fps:
        num, denom = fps.split('/')
        if int(denom) == 0:
            raise ValueError("fps denominator cannot be zero")
        if int(num) == 0:
            raise ValueError("fps numerator cannot be zero")

    # Check for zero/negative values in decimals
    else:
        if float(fps) <= 0:
            raise ValueError("fps must be greater than zero")

    return fps


def extract_frames(
    video_path: Path,
    output_dir: Path | None = None,
    fps: str = "1",
    smart: bool = True,
    dedupe: bool = True,
    dedupe_threshold: int = 5,
) -> Path:
    """
    Extract frames from a video file.

    Args:
        video_path: Path to the video file.
        output_dir: Output directory for frames. Defaults to '{video}-frames/' next to video.
        fps: Frame rate (e.g., "1" for 1fps, "1/2" for 1 frame every 2 seconds).
        smart: If True, filter out "talking head" frames using AI vision.
        dedupe: If True, remove duplicate frames after extraction.
        dedupe_threshold: Hamming distance threshold for deduplication (0-64).

    Returns:
        Path to the output directory containing frames.
    """
    video_path = Path(video_path).resolve()

    if not video_path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")

    # Validate fps parameter before using in subprocess
    fps = _validate_fps(fps)

    # Default output directory: {video_name}-frames/ next to the video
    if output_dir is None:
        output_dir = video_path.parent / f"{video_path.stem}-frames"
    else:
        output_dir = Path(output_dir).resolve()

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Output pattern
    output_pattern = output_dir / "frame_%04d.png"

    # Build ffmpeg command
    cmd = [
        "ffmpeg",
        "-i", str(video_path),
        "-vf", f"fps={fps}",
        "-y",  # Overwrite existing files
        str(output_pattern),
    ]

    # Calculate total passes
    total_passes = 1 + (1 if dedupe else 0) + (1 if smart else 0)
    current_pass = 0
    total_start = time.time()
    initial_count = 0

    print(f"Extracting frames from: {video_path.name}")
    print(f"Output directory: {output_dir}")
    print(f"Frame rate: {fps} fps")
    print()

    # Pass 1: Extract frames
    current_pass += 1
    print(f"[Pass {current_pass}/{total_passes}] Extracting frames (ffmpeg)")
    pass_start = time.time()

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error: ffmpeg failed", file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: ffmpeg not found. Please install ffmpeg.", file=sys.stderr)
        sys.exit(1)

    # Count extracted frames
    frame_count = len(list(output_dir.glob("frame_*.png")))
    initial_count = frame_count
    pass_time = time.time() - pass_start
    print(f"Extracted {frame_count} frames [{pass_time:.1f}s]")

    # Pass 2: Deduplicate (fast, local operation)
    if dedupe and frame_count > 1:
        current_pass += 1
        print()
        print(f"[Pass {current_pass}/{total_passes}] Removing visually identical frames (perceptual hashing)")
        pass_start = time.time()

        deduplicator = FrameDeduplicator(threshold=dedupe_threshold)
        result = deduplicator.find_duplicates(output_dir)

        if result.duplicate_count > 0:
            removed = deduplicator.dedupe_safely(output_dir, result)
            pass_time = time.time() - pass_start
            print(f"{frame_count} -> {result.kept_count} frames ({removed} duplicates removed) [{pass_time:.1f}s]")
            frame_count = result.kept_count
        else:
            pass_time = time.time() - pass_start
            print(f"No duplicates found [{pass_time:.1f}s]")

    # Pass 3: Smart filter (API calls)
    if smart and frame_count > 0:
        current_pass += 1
        print()
        print(f"[Pass {current_pass}/{total_passes}] AI visual analysis (Gemini 2.0 Flash)")
        print("Analyzing each frame for educational value vs promotional content...")
        pass_start = time.time()
        before_smart = frame_count

        try:
            classifier = FrameClassifier()
            frames = sorted(output_dir.glob("frame_*.png"))

            def progress(current, total, name, result):
                label = "keep" if result == "content" else "discard"
                print(f"  [{current}/{total}] {name}: {label}")

            content_frames, person_frames = classifier.filter_frames(frames, progress)

            # Delete person-only frames
            for frame in person_frames:
                frame.unlink()

            # Renumber remaining frames sequentially
            if person_frames:
                remaining = sorted(output_dir.glob("frame_*.png"))
                for i, frame in enumerate(remaining, start=1):
                    new_name = output_dir / f"frame_{i:04d}.png"
                    if frame != new_name:
                        frame.rename(new_name)

            pass_time = time.time() - pass_start
            frame_count = len(content_frames)
            print(f"{before_smart} -> {frame_count} frames ({len(person_frames)} non-educational frames discarded) [{pass_time:.1f}s]")

        except ValueError as e:
            pass_time = time.time() - pass_start
            print(f"Warning: Smart filtering unavailable: {e} [{pass_time:.1f}s]")
            print("Continuing without smart filtering...")

    # Final summary
    total_time = time.time() - total_start
    if initial_count > 0:
        reduction = round((1 - frame_count / initial_count) * 100)
        print()
        print(f"Complete: {initial_count} -> {frame_count} frames ({reduction}% reduction) [{total_time:.1f}s total]")

    return output_dir


def main():
    parser = argparse.ArgumentParser(
        description="Extract frames from video files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s video.mp4                    # Creates video-frames/ folder
  %(prog)s video.mp4 --no-smart         # Skip AI filtering
  %(prog)s video.mp4 --no-dedupe        # Skip deduplication
  %(prog)s video.mp4 --no-smart --no-dedupe  # Raw extraction only
  %(prog)s video.mp4 --fps 1/2          # 1 frame every 2 seconds
  %(prog)s video.mp4 --output my_frames # Custom output directory
""",
    )
    parser.add_argument(
        "video",
        help="Path to video file",
    )
    parser.add_argument(
        "--fps", "-f",
        default="1",
        help="Frame rate: '1' for 1fps, '1/2' for every 2 seconds (default: 1)",
    )
    parser.add_argument(
        "--output", "-o",
        help="Output directory (default: {video}-frames/ next to video)",
    )
    parser.add_argument(
        "--smart", "-s",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="AI filter: remove talking head frames (default: on)",
    )
    parser.add_argument(
        "--dedupe", "-d",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Remove duplicate frames (default: on)",
    )
    parser.add_argument(
        "--threshold", "-t",
        type=int,
        default=5,
        help="Deduplication threshold 0-64 (default: 5)",
    )

    args = parser.parse_args()

    try:
        output_dir = Path(args.output) if args.output else None
        extract_frames(
            video_path=Path(args.video),
            output_dir=output_dir,
            fps=args.fps,
            smart=args.smart,
            dedupe=args.dedupe,
            dedupe_threshold=args.threshold,
        )
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(130)


if __name__ == "__main__":
    main()
