from pathlib import Path

import ffmpeg

from config import TEMP_DIR
from utils.logger import get_logger


class AudioExtractor:
    """
    Extracts audio from a video file using FFmpeg.
    """

    def __init__(self) -> None:
        self.logger = get_logger(__name__)

    def extract(self, video_path: Path) -> Path:
        """
        Extract audio from the given video.

        Args:
            video_path: Path to the input video.

        Returns:
            Path to the extracted WAV file.
        """

        if not video_path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")

        output_audio = TEMP_DIR / f"{video_path.stem}.wav"

        self.logger.info("Extracting audio...")

        (
            ffmpeg
            .input(str(video_path))
            .output(
                str(output_audio),
                ac=1,
                ar=16000,
                vn=None,
            )
            .overwrite_output()
            .run(quiet=True)
        )

        self.logger.info(f"Audio saved to: {output_audio}")

        return output_audio