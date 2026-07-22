"""
media_quality/loudness_normalizer.py

EBU R128 loudness normalization for the final stitched dubbed audio,
via FFmpeg's loudnorm filter, so output volume is consistent regardless
of source/TTS gain variance.
"""
import subprocess
from pathlib import Path

from config import settings as config
from app.utils.logger import get_logger

logger = get_logger(__name__)


def normalize_loudness(audio_path: Path, target_lufs: float | None = None) -> Path:
    """
    Normalize an audio file's integrated loudness in place.

    Args:
        audio_path: Path to the audio file to normalize.
        target_lufs: Target integrated loudness in LUFS. Defaults to
            config.LOUDNESS_TARGET_LUFS.

    Returns:
        The path to the normalized audio file (same as audio_path).
    """
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    target = target_lufs if target_lufs is not None else getattr(config, "LOUDNESS_TARGET_LUFS", -16.0)
    temp_output = audio_path.with_suffix(".normalized.wav")

    cmd = [
        "ffmpeg", "-y",
        "-i", str(audio_path),
        "-af", f"loudnorm=I={target}:TP=-1.5:LRA=11",
        str(temp_output),
    ]

    logger.info(f"Normalizing loudness of {audio_path.name} to {target} LUFS...")
    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError as error:
        logger.error(f"Loudness normalization failed: {error.stderr.decode(errors='ignore')}")
        raise RuntimeError("FFmpeg loudness normalization failed.") from error

    temp_output.replace(audio_path)
    logger.info("Loudness normalization completed.")
    return audio_path
