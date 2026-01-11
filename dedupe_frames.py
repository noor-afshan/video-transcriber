#!/usr/bin/env python3
"""Remove duplicate frames from a directory using perceptual hashing."""

import argparse
import sys
import time
from pathlib import Path

from modules.deduplicator import FrameDeduplicator
from modules.frame_classifier import FrameClassifier


def dedupe_frames(
    directory: Path,
    smart: bool = True,
    threshold: int = 5,
    dry_run: bool = False,
) -> tuple[int, int]:
    """
    Remove duplicate frames from a directory.

    Args:
        directory: Path to directory containing frames.
        smart: If True, filter out "talking head" frames using AI vision.
        threshold: Hamming distance threshold (0-64). Lower = more strict.
        dry_run: If True, only show what would be deleted.

    Returns:
        Tuple of (kept_count, deleted_count).
    """
    directory = Path(directory).resolve()

    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    if not directory.is_dir():
        raise ValueError(f"Not a directory: {directory}")

    deduplicator = FrameDeduplicator(threshold=threshold)

    # Calculate total passes
    total_passes = 1 + (1 if smart else 0)
    current_pass = 0
    total_start = time.time()

    print(f"Processing: {directory}")
    print(f"Threshold: {threshold} (Hamming distance)")
    print()

    # Count initial frames
    initial_count = len(list(directory.glob("frame_*.png")))
    frame_count = initial_count

    # Pass 1: Dedupe (fast, local operation)
    current_pass += 1
    print(f"[Pass {current_pass}/{total_passes}] Removing visually identical frames (perceptual hashing)")
    pass_start = time.time()

    result = deduplicator.find_duplicates(directory)

    if result.duplicate_count == 0:
        pass_time = time.time() - pass_start
        print(f"No duplicates found. All {result.kept_count} frames are unique [{pass_time:.1f}s]")
    else:
        if dry_run:
            pass_time = time.time() - pass_start
            print(f"[DRY RUN] Would remove {result.duplicate_count} duplicates, keep {result.kept_count} [{pass_time:.1f}s]")
        else:
            removed = deduplicator.dedupe_safely(directory, result)
            pass_time = time.time() - pass_start
            print(f"{frame_count} → {result.kept_count} frames ({removed} duplicates removed) [{pass_time:.1f}s]")
            frame_count = result.kept_count

    # Pass 2: Smart filter (API calls)
    if smart:
        frames = sorted(directory.glob("frame_*.png"))
        if frames:
            current_pass += 1
            print()
            print(f"[Pass {current_pass}/{total_passes}] Filtering non-content frames")
            print("Using Gemini 2.0 Flash AI via API...")
            pass_start = time.time()
            before_smart = len(frames)

            try:
                classifier = FrameClassifier()

                def progress(current, total, name, cls_result):
                    print(f"  [{current}/{total}] {name}: {cls_result}")

                content_frames, person_frames = classifier.filter_frames(frames, progress)

                if dry_run:
                    pass_time = time.time() - pass_start
                    print(f"[DRY RUN] Would remove {len(person_frames)} talking heads, keep {len(content_frames)} [{pass_time:.1f}s]")
                else:
                    # Delete person-only frames
                    for frame in person_frames:
                        frame.unlink()

                    # Renumber remaining frames sequentially
                    if person_frames:
                        remaining = sorted(directory.glob("frame_*.png"))
                        for i, frame in enumerate(remaining, start=1):
                            new_name = directory / f"frame_{i:04d}.png"
                            if frame != new_name:
                                frame.rename(new_name)

                    pass_time = time.time() - pass_start
                    frame_count = len(content_frames)
                    print(f"{before_smart} → {frame_count} frames ({len(person_frames)} talking heads removed) [{pass_time:.1f}s]")

            except ValueError as e:
                pass_time = time.time() - pass_start
                print(f"Warning: Smart filtering unavailable: {e} [{pass_time:.1f}s]")
                print("Continuing without smart filtering...")

    # Final summary
    total_time = time.time() - total_start
    final_count = len(list(directory.glob("frame_*.png")))
    if initial_count > 0 and not dry_run:
        reduction = round((1 - final_count / initial_count) * 100)
        print()
        print(f"Complete: {initial_count} → {final_count} frames ({reduction}% reduction) [{total_time:.1f}s total]")

    return final_count, result.duplicate_count


def main():
    parser = argparse.ArgumentParser(
        description="Remove duplicate frames using perceptual hashing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s frames/                     # Dedupe + smart filter (default)
  %(prog)s frames/ --no-smart          # Skip AI filtering
  %(prog)s frames/ --dry-run           # Preview what would be deleted
  %(prog)s frames/ --threshold 3       # More strict (fewer duplicates detected)
  %(prog)s frames/ --threshold 10      # More permissive (more duplicates detected)

Threshold guide:
  0     = Exact matches only
  1-2   = Very strict (minor compression differences)
  3-5   = Recommended for video frames
  6-10  = Permissive (visually similar but not identical)
  11+   = Very permissive (may catch false positives)
""",
    )
    parser.add_argument(
        "directory",
        help="Directory containing frame images",
    )
    parser.add_argument(
        "--smart", "-s",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="AI filter: remove talking head frames (default: on)",
    )
    parser.add_argument(
        "--threshold", "-t",
        type=int,
        default=5,
        help="Hamming distance threshold 0-64 (default: 5)",
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Show what would be deleted without deleting",
    )

    args = parser.parse_args()

    if args.threshold < 0 or args.threshold > 64:
        print("Error: threshold must be between 0 and 64", file=sys.stderr)
        sys.exit(1)

    try:
        dedupe_frames(
            directory=Path(args.directory),
            smart=args.smart,
            threshold=args.threshold,
            dry_run=args.dry_run,
        )
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(130)


if __name__ == "__main__":
    main()
