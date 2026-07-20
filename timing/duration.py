"""
Audio duration calculation engine.

Responsible for computing expected segment duration and measuring actual audio
file duration using ffprobe.
"""

from pathlib import Path
import subprocess
from utils.logger import get_logger


logger = get_logger(__name__)


def calculate_expected_duration(start: float, end: float) -> float:
    """
    Calculate the expected duration of a segment in seconds.

    Args:
        start: Start timestamp of the segment.
        end: End timestamp of the segment.

    Returns:
        The expected duration in seconds.
    """
    return max(0.0, end - start)


def calculate_actual_duration(audio_path: Path) -> float:
    """
    Measure the actual duration of an audio file in seconds using ffprobe.

    Args:
        audio_path: Path to the target audio file (e.g. MP3).

    Returns:
        The actual measured duration in seconds.

    Raises:
        FileNotFoundError: If the audio file does not exist.
        RuntimeError: If ffprobe execution fails or yields invalid output.
    """
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found at: {audio_path}")

    # Call ffprobe to fetch the format duration attribute
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(audio_path)
    ]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        duration_str = result.stdout.strip()
        if not duration_str:
            raise ValueError("Empty output returned from ffprobe.")
        return float(duration_str)
    except Exception as error:
        logger.error(f"ffprobe duration measurement failed for {audio_path}: {error}")
        raise RuntimeError(
            f"Failed to measure duration of audio file {audio_path.name} via ffprobe: {error}"
        ) from error
