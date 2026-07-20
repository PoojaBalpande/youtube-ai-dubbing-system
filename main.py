from audio.extractor import AudioExtractor
from downloader.youtube import YouTubeDownloader
from transcription.whisper_engine import WhisperEngine
from translation.translator import Translator
from utils.logger import get_logger
from tts.tts import TextToSpeech


def main() -> None:
    """
    Entry point of the application.
    """

    logger = get_logger(__name__)

    url = input("Enter YouTube URL: ").strip()

    downloader = YouTubeDownloader()
    extractor = AudioExtractor()
    transcriber = WhisperEngine()
    
    try:
        # Download video
        video_path = downloader.download(url)
        logger.info(f"Video saved to: {video_path}")

        # Extract audio
        audio_path = extractor.extract(video_path)
        logger.info(f"Audio saved to: {audio_path}")

        # Transcribe audio
        result = transcriber.transcribe(audio_path)

        transcript_path = transcriber.save_transcript(result["text"])
        logger.info(f"Transcript saved at: {transcript_path}")

        # Create translator only when needed to avoid unnecessary resource usage
        translator = Translator()

        # Translate transcript
        translated_text = translator.translate(result["text"])

        translation_path = translator.save_translation(
            translated_text
        )
        
        # Synthesize translated text to speech
        tts = TextToSpeech()

        audio_path = tts.synthesize(translated_text)

        print(f"TTS Audio Saved: {audio_path}")

        logger.info(
            f"Translated transcript saved at: {translation_path}"
        )

        logger.info("Pipeline completed successfully.")

    except Exception as error:
        logger.exception(f"Application failed: {error}")


if __name__ == "__main__":
    main()