"""Frame classification module using Gemini vision."""

import os
from pathlib import Path
from typing import Callable

from google import genai
from PIL import Image


class FrameClassifier:
    """Classifies frames as useful content or just a talking head using Gemini."""

    CLASSIFICATION_PROMPT = """Classify this video frame for educational value:

CONTENT (keep): Shows learning material - code, diagrams, UI demos, documents, technical slides.

DISCARD (remove): Shows promotional or low-value visuals - talking heads, title cards, tweet screenshots, sponsor segments, intro/outro graphics, "subscribe" overlays.

Rule: Text that is promotional or decorative (not teaching a concept) = DISCARD.

Reply with one word: CONTENT or DISCARD"""

    def __init__(self, api_key: str | None = None):
        """
        Initialize the classifier.

        Args:
            api_key: Google API key. If not provided, uses GOOGLE_API_KEY env var.
        """
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Google API key required. Set GOOGLE_API_KEY or GEMINI_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self.client = genai.Client(api_key=self.api_key)

    def classify_frame(self, image_path: Path) -> str:
        """
        Classify a single frame.

        Args:
            image_path: Path to the image file.

        Returns:
            "content" or "person"
        """
        try:
            img = Image.open(image_path)
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[img, self.CLASSIFICATION_PROMPT],
            )
            result = response.text.strip().upper()

            if "CONTENT" in result:
                return "content"
            elif "DISCARD" in result:
                return "person"  # Keep internal value as "person" for compatibility
            elif "DELETE" in result:
                return "person"  # Backward compatibility
            elif "PERSON" in result:
                return "person"  # Backward compatibility
            else:
                # If unclear, keep the frame to be safe
                return "content"
        except Exception as e:
            print(f"Warning: Could not classify {image_path.name}: {e}")
            # On error, keep the frame to be safe
            return "content"

    def filter_frames(
        self,
        frames: list[Path],
        progress_callback: Callable | None = None,
    ) -> tuple[list[Path], list[Path]]:
        """
        Filter frames, keeping only content frames.

        Args:
            frames: List of frame paths to classify.
            progress_callback: Optional callback(current, total, frame_name, result)

        Returns:
            Tuple of (content_frames, person_frames)
        """
        content_frames = []
        person_frames = []

        for i, frame in enumerate(frames):
            result = self.classify_frame(frame)

            if result == "content":
                content_frames.append(frame)
            else:
                person_frames.append(frame)

            if progress_callback:
                progress_callback(i + 1, len(frames), frame.name, result)

        return content_frames, person_frames
