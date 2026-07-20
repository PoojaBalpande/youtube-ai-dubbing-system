"""
audio/merger.py

Merges the original video with translated audio
to create the final dubbed video.
"""

from pathlib import Path
import subprocess
from unittest import result

from utils.logger import get_logger


class AudioMerger:
    """
    Handles replacing the original audio track
    with the translated English audio.
    """

    def __init__(self):
        self.logger = get_logger(__name__)

    def merge_audio(
        self,
        video_path: Path,
        audio_path: Path,
        output_path: Path,
    ) -> Path:
        """
        Merge original video with translated audio.

        Args:
            video_path: Path to original MP4
            audio_path: Path to translated MP3
            output_path: Path for dubbed MP4

        Returns:
            Path to dubbed video.
        """

        self.logger.info("Starting audio merge...")

        # Check input files
        if not video_path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")

        if not audio_path.exists():
            raise FileNotFoundError(f"Audio not found: {audio_path}")

        # Create output directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        import config
        video_codec = getattr(config, "VIDEO_CODEC", "copy")
        audio_codec = getattr(config, "AUDIO_CODEC", "aac")
        faststart = getattr(config, "FASTSTART", True)

        command = [
            "ffmpeg",
            "-i", str(video_path),
            "-i", str(audio_path),
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", video_codec,
            "-c:a", audio_codec,
            "-ar", "48000",
            "-ac", "2",
        ]

        if faststart:
            command += ["-movflags", "+faststart"]

        command += ["-y", str(output_path)]

        self.logger.info("Running FFmpeg...")

        try:
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
            )
            
            if result.stdout:
                self.logger.debug(f"FFmpeg stdout: {result.stdout.strip()}")
            if result.stderr:
                self.logger.debug(f"FFmpeg stderr: {result.stderr.strip()}")

            self.logger.info("Audio merged successfully.")
            self.logger.info(f"Dubbed video saved to: {output_path}")

        except subprocess.CalledProcessError as e:
            self.logger.error("FFmpeg failed.")
            self.logger.error(e.stderr)
            raise RuntimeError("Audio merge failed.") from e

        if not output_path.exists():
            raise RuntimeError("Output video was not created.")

        return output_path