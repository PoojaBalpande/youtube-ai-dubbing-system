"""
Audio conversion utilities.

Provides conversion between formats (e.g. MP3 to WAV) and normalizes sample
rates and channel layouts using FFmpeg.
"""

from pathlib import Path
import subprocess
from utils.logger import get_logger


logger = get_logger(__name__)


def convert_mp3_to_wav(
    mp3_path: Path,
    wav_path: Path,
    sample_rate: int = 16000,
    channels: int = 1
) -> Path:
    """
    Convert an MP3 file to a standardized PCM WAV file using FFmpeg.

    Standardizes to:
    - Sample rate: Configurable (default: 16000 Hz)
    - Channels: Configurable (default: 1 mono)
    - Audio codec: 16-bit PCM WAV (pcm_s16le)

    Args:
        mp3_path: Path to the input MP3 file.
        wav_path: Target path for the output WAV file.
        sample_rate: Target sample rate in Hz.
        channels: Target number of audio channels.

    Returns:
        The Path to the generated WAV file.

    Raises:
        FileNotFoundError: If the input MP3 file is missing.
        RuntimeError: If the FFmpeg conversion fails.
    """
    if not mp3_path.exists():
        raise FileNotFoundError(f"Input MP3 file not found: {mp3_path}")

    wav_path.parent.mkdir(parents=True, exist_ok=True)

    # ffmpeg standard command to convert and normalize formats
    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(mp3_path),
        "-ar", str(sample_rate),
        "-ac", str(channels),
        "-c:a", "pcm_s16le",
        str(wav_path)
    ]

    try:
        logger.debug(f"Converting segment: {mp3_path.name} -> {wav_path.name}")
        subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        return wav_path
    except subprocess.CalledProcessError as error:
        error_msg = error.stderr.decode("utf-8", errors="ignore")
        logger.error(f"FFmpeg conversion failed: {error_msg}")
        raise RuntimeError(f"FFmpeg failed to convert MP3 to WAV: {error_msg}") from error
