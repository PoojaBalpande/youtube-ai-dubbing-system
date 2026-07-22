"""
media_quality/background_music.py

Remixes an isolated background-music stem (from vocal_isolation.py)
underneath the stitched dubbed vocal track.
"""
import subprocess
from pathlib import Path

from app.utils.logger import get_logger

logger = get_logger(__name__)


def remix_with_background(dubbed_vocals_path: Path, background_path: Path, output_path: Path) -> Path:
    """
    Mix the dubbed vocal track with a preserved background-music stem.

    Args:
        dubbed_vocals_path: The stitched, synchronized dubbed vocal WAV.
        background_path: The background stem produced by vocal_isolation.
        output_path: Destination for the mixed track.

    Returns:
        The path to the mixed audio file.
    """
    if not dubbed_vocals_path.exists() or not background_path.exists():
        raise FileNotFoundError("Both dubbed vocals and background stem must exist to remix.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-i", str(dubbed_vocals_path),
        "-i", str(background_path),
        "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=first:dropout_transition=2",
        str(output_path),
    ]

    logger.info("Remixing dubbed vocals with preserved background music...")
    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError as error:
        logger.error(f"Background remix failed: {error.stderr.decode(errors='ignore')}")
        raise RuntimeError("FFmpeg background remix failed.") from error

    return output_path
