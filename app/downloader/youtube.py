from pathlib import Path
from typing import Dict

import yt_dlp

from config.settings import DOWNLOAD_DIR
from app.utils.logger import get_logger


class YouTubeDownloader:
    """
    Handles downloading YouTube videos using yt-dlp.
    """

    def __init__(self) -> None:
        self.logger = get_logger(__name__)
        self.download_dir = DOWNLOAD_DIR

    def validate_url(self, url: str) -> bool:
        """
        Basic validation for YouTube URLs.
        """
        return (
            url.startswith("https://www.youtube.com/")
            or url.startswith("https://youtu.be/")
        )

    def get_video_info(self, url: str) -> Dict:
        """
        Retrieve metadata without downloading the video.
        """
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            return ydl.extract_info(url, download=False)

    def download(self, url: str) -> Path:
        """
        Download a YouTube video.

        Args:
            url: YouTube video URL.

        Returns:
            Path to the downloaded video.
        """
        if not self.validate_url(url):
            raise ValueError("Invalid YouTube URL.")

        self.logger.info("Fetching video information...")

        info = self.get_video_info(url)

        self.logger.info(f"Title: {info['title']}")
        self.logger.info(f"Duration: {info['duration']} seconds")

        from config import settings as config
        ytdlp_format = getattr(config, "YTDLP_FORMAT", "bestvideo+bestaudio/best")
        ytdlp_merge = getattr(config, "YTDLP_MERGE_OUTPUT_FORMAT", "mp4")

        output_template = str(self.download_dir / "%(title)s.%(ext)s")

        ydl_opts = {
            "format": ytdlp_format,
            "outtmpl": output_template,
            "merge_output_format": ytdlp_merge,
        }

        self.logger.info("Downloading video...")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        downloaded_file = Path(
            ydl.prepare_filename(info)
        ).with_suffix(".mp4")

        self.logger.info("Download completed successfully.")

        return downloaded_file