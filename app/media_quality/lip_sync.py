"""
media_quality/lip_sync.py

Extension point for lip-sync correction (e.g. Wav2Lip-style models).
"""
from pathlib import Path


def resync_lips(video_path: Path, dubbed_audio_path: Path, output_path: Path) -> Path:
    """
    Re-render mouth movement in `video_path` to match `dubbed_audio_path`.

    Raises:
        NotImplementedError: No lip-sync backend is wired in yet.
    """
    raise NotImplementedError(
        "Lip-sync correction is a scaffolded extension point (Milestone 12). "
        "Integrate a Wav2Lip-style model here when this milestone is picked up."
    )
