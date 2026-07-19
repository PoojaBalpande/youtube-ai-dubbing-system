from audio.extractor import AudioExtractor
from downloader.youtube import YouTubeDownloader
from utils.logger import get_logger


def main() -> None:
    """
    Entry point of the application.
    """

    logger = get_logger(__name__)

    url = input("Enter YouTube URL: ").strip()

    downloader = YouTubeDownloader()
    extractor = AudioExtractor()

    try:
        # Download video
        video_path = downloader.download(url)
        logger.info(f"Video saved to: {video_path}")

        # Extract audio
        audio_path = extractor.extract(video_path)
        logger.info(f"Audio saved to: {audio_path}")

    except Exception as error:
        logger.exception(f"Application failed: {error}")


if __name__ == "__main__":
    main()