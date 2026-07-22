"""
media_quality/vocal_isolation.py

Extension point for source separation (e.g. Demucs) to split original
audio into vocal and background-music stems, for later remixing under
the dubbed vocal track (see background_music.py).
"""
from pathlib import Path


def separate_vocals(audio_path: Path, output_dir: Path) -> dict:
    """
    Split an audio file into "vocals" and "background" stems.

    Raises:
        NotImplementedError: Install 'demucs' and implement this function
            around demucs.separate.main([...]) to enable it.
    """
    raise NotImplementedError(
        "Vocal isolation is a scaffolded extension point (Milestone 12). "
        "Install 'demucs' and implement separate_vocals() to enable it."
    )
