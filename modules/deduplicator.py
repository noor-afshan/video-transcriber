"""Frame deduplication module using perceptual hashing."""

import shutil
from pathlib import Path
from dataclasses import dataclass

from PIL import Image
import imagehash


@dataclass
class DedupeResult:
    """Result of frame deduplication."""
    kept: list[Path]
    duplicates: list[Path]

    @property
    def kept_count(self) -> int:
        return len(self.kept)

    @property
    def duplicate_count(self) -> int:
        return len(self.duplicates)


class FrameDeduplicator:
    """Identifies and removes duplicate frames using dHash perceptual hashing."""

    SUPPORTED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}

    def __init__(self, threshold: int = 5, hash_size: int = 8):
        """
        Initialize the deduplicator.

        Args:
            threshold: Maximum Hamming distance for frames to be considered duplicates (0-64).
                       Lower = more strict, higher = more permissive.
                       Recommended: 2-5 for video frames.
            hash_size: Size of the hash (default 8 produces 64-bit hash).
        """
        self.threshold = threshold
        self.hash_size = hash_size

    def find_duplicates(self, directory: Path | str) -> DedupeResult:
        """
        Find duplicate frames in a directory using sequential comparison.

        Args:
            directory: Path to directory containing frame images.

        Returns:
            DedupeResult with lists of frames to keep and duplicates to remove.
        """
        directory = Path(directory)

        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        # Get sorted list of image files
        frames = self._get_sorted_frames(directory)

        if not frames:
            return DedupeResult(kept=[], duplicates=[])

        if len(frames) == 1:
            return DedupeResult(kept=frames, duplicates=[])

        # Sequential comparison - compare each frame to the last "kept" frame
        kept = [frames[0]]
        duplicates = []

        last_kept_hash = self._compute_hash(frames[0])

        for frame in frames[1:]:
            current_hash = self._compute_hash(frame)

            if current_hash is None:
                # Couldn't compute hash, keep the frame to be safe
                kept.append(frame)
                continue

            if last_kept_hash is None:
                # Previous frame had no hash, keep this one
                kept.append(frame)
                last_kept_hash = current_hash
                continue

            # Calculate Hamming distance
            distance = last_kept_hash - current_hash

            if distance <= self.threshold:
                # Similar to previous kept frame - mark as duplicate
                duplicates.append(frame)
            else:
                # Different enough - keep it
                kept.append(frame)
                last_kept_hash = current_hash

        return DedupeResult(kept=kept, duplicates=duplicates)

    def _get_sorted_frames(self, directory: Path) -> list[Path]:
        """Get sorted list of image files in directory."""
        frames = []
        for f in directory.iterdir():
            if f.is_file() and f.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                frames.append(f)
        return sorted(frames, key=lambda p: p.name.lower())

    def _compute_hash(self, image_path: Path) -> imagehash.ImageHash | None:
        """Compute dHash for an image file."""
        try:
            with Image.open(image_path) as img:
                return imagehash.dhash(img, hash_size=self.hash_size)
        except Exception as e:
            print(f"Warning: Could not hash {image_path.name}: {e}")
            return None

    def dedupe_safely(self, directory: Path | str, result: DedupeResult) -> int:
        """
        Safely remove duplicates using a staging folder approach.

        Process:
        1. Copy unique frames to deduped/ subfolder (with sequential naming)
        2. Delete all images in source folder
        3. Move deduped images back to source folder
        4. Delete deduped/ folder

        Args:
            directory: Path to the frames directory.
            result: DedupeResult from find_duplicates().

        Returns:
            Number of duplicates removed.
        """
        directory = Path(directory)
        deduped_dir = directory / "deduped"

        # Step 1: Copy unique frames to deduped/ with sequential naming
        deduped_dir.mkdir(exist_ok=True)

        # Get extension from first kept frame
        ext = result.kept[0].suffix if result.kept else ".png"

        for i, frame in enumerate(result.kept, start=1):
            new_name = f"frame_{i:04d}{ext}"
            shutil.copy2(frame, deduped_dir / new_name)

        # Step 2: Delete all images in source folder
        for f in directory.iterdir():
            if f.is_file() and f.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                f.unlink()

        # Step 3: Move deduped images back to source folder
        for f in deduped_dir.iterdir():
            shutil.move(str(f), directory / f.name)

        # Step 4: Delete deduped/ folder
        deduped_dir.rmdir()

        return result.duplicate_count

    def delete_duplicates(self, result: DedupeResult) -> int:
        """
        Delete duplicate files from disk (legacy method).

        Args:
            result: DedupeResult from find_duplicates().

        Returns:
            Number of files deleted.
        """
        deleted = 0
        for dup in result.duplicates:
            try:
                dup.unlink()
                deleted += 1
            except Exception as e:
                print(f"Warning: Could not delete {dup.name}: {e}")
        return deleted
