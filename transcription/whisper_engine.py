from pathlib import Path
import whisper
from utils.logger import get_logger
from config import (
    WHISPER_MODEL,
    DEVICE,
    TRANSCRIPT_FILE,
    TRANSCRIPTION_LANGUAGE,
    BEAM_SIZE,
    TEMPERATURE,
)

logger = get_logger(__name__)

class WhisperEngine:
    """Speech-to-Text engine using OpenAI Whisper."""

    def __init__(self) -> None:
        """
        Initialize the Whisper model.
        """
        
        logger.info(f"Loading Whisper model: {WHISPER_MODEL}")

        self.model = whisper.load_model(
            WHISPER_MODEL,
            device=DEVICE
        )

        logger.info("Whisper model loaded successfully.")

    def transcribe(self, audio_path: Path) -> dict:
        """
        Transcribe an audio file using Whisper.
        """

        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        logger.info(f"Starting transcription: {audio_path.name}")

        try:
            result = self.model.transcribe(
                str(audio_path),
                language=TRANSCRIPTION_LANGUAGE,
                beam_size=BEAM_SIZE,
                temperature=TEMPERATURE,
            )

            logger.info("Transcription completed successfully.")

            return {
                "text": result["text"].strip(),
                "language": result["language"],
                "segments": result["segments"],
            }

        except Exception as error:
            logger.exception(f"Transcription failed: {error}")
            raise

    def save_transcript(self, text: str) -> Path:
        """
        Save transcript text to a file.
        """

        TRANSCRIPT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(TRANSCRIPT_FILE, "w", encoding="utf-8") as file:
            file.write(text)

        logger.info(f"Transcript saved to: {TRANSCRIPT_FILE}")

        return TRANSCRIPT_FILE