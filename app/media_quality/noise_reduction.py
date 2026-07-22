"""
media_quality/noise_reduction.py

Applies FFmpeg's afftdn (adaptive FFT denoiser) filter to reduce
background hiss/noise.
"""
import subprocess
from pathlib import Path

from app.utils.logger import get_logger

logger = get_logger(__name__)


def reduce_noise(audio_path: Path) -> Path:
    """
    Apply spectral noise reduction to an audio file in place.

    Args:
        audio_path: Path to the audio file to denoise.

    Returns:
        The path to the denoised audio file (same as audio_path).
    """
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    temp_output = audio_path.with_suffix(".denoised.wav")
    cmd = ["ffmpeg", "-y", "-i", str(audio_path), "-af", "afftdn", str(temp_output)]

    logger.info(f"Reducing noise in {audio_path.name}...")
    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError as error:
        logger.error(f"Noise reduction failed: {error.stderr.decode(errors='ignore')}")
        raise RuntimeError("FFmpeg noise reduction failed.") from error

    temp_output.replace(audio_path)
    logger.info("Noise reduction completed.")
    return audio_path
