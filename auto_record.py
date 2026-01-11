#!/usr/bin/env python3
"""
Auto-record OBS when Teams meeting starts.
Monitors for Teams meeting windows and controls OBS via WebSocket.
"""

import argparse
import json
import time
import sys
import subprocess
from pathlib import Path

import win32gui
import win32process
import psutil

try:
    import obsws_python as obs
except ImportError:
    print("Error: obsws-python not installed. Run: pip install obsws-python")
    sys.exit(1)


def load_config():
    """Load config from config.json."""
    config_path = Path(__file__).parent / "config.json"
    if config_path.exists():
        with open(config_path, "r") as f:
            return json.load(f)
    return {}


# Teams meeting window detection patterns
MEETING_PATTERNS = [
    "Meeting with",
    "Meeting in",
]

# Window titles to exclude (not actual meetings - main Teams app windows)
EXCLUDE_PATTERNS = [
    "Microsoft Teams (work or school)",
    "Microsoft Teams - Free",
    "| Chat |",
    "| Calendar |",
    "| Teams |",
    "| Activity |",
    "| Calls |",
    "| Files |",
]


def find_teams_meeting_window():
    """Find active Teams meeting window. Returns window title if found, None otherwise."""
    meeting_window = None

    def callback(hwnd, _):
        nonlocal meeting_window
        if not win32gui.IsWindowVisible(hwnd):
            return True

        title = win32gui.GetWindowText(hwnd)
        if not title:
            return True

        # Skip excluded windows
        for exclude in EXCLUDE_PATTERNS:
            if exclude in title:
                return True

        # Check for meeting patterns
        for pattern in MEETING_PATTERNS:
            if pattern in title:
                # Verify it's actually Teams process
                try:
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    proc = psutil.Process(pid)
                    proc_name = proc.name().lower()
                    if "teams" in proc_name or "ms-teams" in proc_name or "python" in proc_name:
                        meeting_window = title
                        return False  # Stop enumeration
                except Exception:
                    # If we can't verify process, still match on title
                    meeting_window = title
                    return False
        return True

    try:
        win32gui.EnumWindows(callback, None)
    except Exception:
        pass  # Ignore enumeration errors
    return meeting_window


class OBSController:
    """Controls OBS recording via WebSocket."""

    def __init__(self, host: str = "localhost", port: int = 4455, password: str = ""):
        self.host = host
        self.port = port
        self.password = password
        self.client = None

    def connect(self) -> bool:
        """Connect to OBS WebSocket. Returns True on success."""
        try:
            self.client = obs.ReqClient(
                host=self.host,
                port=self.port,
                password=self.password,
                timeout=5
            )
            print(f"Connected to OBS at {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Failed to connect to OBS: {e}")
            print("Make sure OBS is running and WebSocket Server is enabled:")
            print("  Tools -> WebSocket Server Settings -> Enable WebSocket Server")
            return False

    def is_recording(self) -> bool:
        """Check if OBS is currently recording."""
        if not self.client:
            return False
        try:
            status = self.client.get_record_status()
            return status.output_active
        except Exception:
            return False

    def start_recording(self) -> bool:
        """Start OBS recording. Returns True on success."""
        if not self.client:
            return False
        try:
            self.client.start_record()
            return True
        except Exception as e:
            print(f"Failed to start recording: {e}")
            return False

    def stop_recording(self) -> str | None:
        """Stop OBS recording. Returns output file path on success."""
        if not self.client:
            return None
        try:
            result = self.client.stop_record()
            return result.output_path
        except Exception as e:
            print(f"Failed to stop recording: {e}")
            return None

    def disconnect(self):
        """Disconnect from OBS."""
        if self.client:
            try:
                self.client.base_client.ws.close()
            except Exception:
                pass
            self.client = None


def run_transcription(video_path: str, args: argparse.Namespace):
    """Run transcription on the recorded video."""
    script_dir = Path(__file__).parent
    transcribe_script = script_dir / "transcribe_meeting.py"

    if not transcribe_script.exists():
        print(f"Transcription script not found: {transcribe_script}")
        return

    cmd = [sys.executable, str(transcribe_script), video_path]

    if args.no_diarize:
        cmd.append("--no-diarize")
    if args.model:
        cmd.extend(["--model", args.model])
    if args.cpu:
        cmd.append("--cpu")

    print(f"\nStarting transcription: {' '.join(cmd)}")
    subprocess.run(cmd)


def main():
    # Load config for defaults
    config = load_config()
    obs_config = config.get("obs", {})

    parser = argparse.ArgumentParser(
        description="Auto-record OBS when Teams meeting starts"
    )
    parser.add_argument(
        "--host", default=obs_config.get("host", "localhost"),
        help="OBS WebSocket host (default: from config or localhost)"
    )
    parser.add_argument(
        "--port", type=int, default=obs_config.get("port", 4455),
        help="OBS WebSocket port (default: from config or 4455)"
    )
    parser.add_argument(
        "--password", default=obs_config.get("password", ""),
        help="OBS WebSocket password (default: from config)"
    )
    parser.add_argument(
        "--poll-interval", type=int, default=5,
        help="Seconds between window checks (default: 5)"
    )
    parser.add_argument(
        "--transcribe", action="store_true",
        help="Auto-transcribe when recording stops"
    )
    parser.add_argument(
        "--no-diarize", action="store_true",
        help="Skip speaker diarization in transcription"
    )
    parser.add_argument(
        "--model", default=None,
        help="Whisper model for transcription (default: from config)"
    )
    parser.add_argument(
        "--cpu", action="store_true",
        help="Use CPU backend for transcription"
    )

    args = parser.parse_args()

    # Connect to OBS
    controller = OBSController(args.host, args.port, args.password)
    if not controller.connect():
        sys.exit(1)

    print(f"\nMonitoring for Teams meetings (checking every {args.poll_interval}s)")
    print("Press Ctrl+C to stop\n")

    was_in_meeting = False
    current_meeting = None

    try:
        while True:
            meeting_window = find_teams_meeting_window()
            in_meeting = meeting_window is not None

            if in_meeting and not was_in_meeting:
                # Meeting started
                current_meeting = meeting_window
                print(f"[{time.strftime('%H:%M:%S')}] Meeting detected: {meeting_window}")

                if not controller.is_recording():
                    if controller.start_recording():
                        print(f"[{time.strftime('%H:%M:%S')}] Started recording")
                    else:
                        print(f"[{time.strftime('%H:%M:%S')}] Failed to start recording")
                else:
                    print(f"[{time.strftime('%H:%M:%S')}] Already recording")

            elif not in_meeting and was_in_meeting:
                # Meeting ended
                print(f"[{time.strftime('%H:%M:%S')}] Meeting ended: {current_meeting}")

                if controller.is_recording():
                    output_path = controller.stop_recording()
                    if output_path:
                        print(f"[{time.strftime('%H:%M:%S')}] Stopped recording: {output_path}")

                        if args.transcribe:
                            run_transcription(output_path, args)
                    else:
                        print(f"[{time.strftime('%H:%M:%S')}] Failed to stop recording")

                current_meeting = None

            was_in_meeting = in_meeting
            time.sleep(args.poll_interval)

    except KeyboardInterrupt:
        print("\n\nStopping...")

        # Stop recording if active
        if controller.is_recording():
            output_path = controller.stop_recording()
            if output_path:
                print(f"Stopped recording: {output_path}")
                if args.transcribe:
                    run_transcription(output_path, args)

        controller.disconnect()
        print("Done")


if __name__ == "__main__":
    main()
