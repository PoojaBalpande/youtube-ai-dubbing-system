from pathlib import Path
import asyncio

import edge_tts

from config import (
    TTS_VOICE,
    TTS_RATE,
    TTS_OUTPUT_FILE,
)
from utils.logger import get_logger


logger = get_logger(__name__)


class TextToSpeech:
    """
    Handles text-to-speech synthesis using Microsoft Edge TTS.
    """

    async def _generate_speech(
        self,
        text: str,
        output_path: Path,
    ) -> None:
        """
        Internal asynchronous method that generates speech.
        """

        communicate = edge_tts.Communicate(
            text=text,
            voice=TTS_VOICE,
            rate=TTS_RATE,
        )

        await communicate.save(str(output_path))

    def synthesize(
        self,
        text: str,
        output_path: Path = TTS_OUTPUT_FILE,
    ) -> Path:
        """
        Converts text into speech and saves it as an audio file.
        """

        if not text.strip():
            raise ValueError("Input text cannot be empty.")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info("Generating speech...")

        try:
            asyncio.run(
                self._generate_speech(
                    text=text,
                    output_path=output_path,
                )
            )

        except Exception as e:
            logger.exception("Speech generation failed.")
            raise RuntimeError("Failed to generate speech.") from e

        logger.info(f"Speech saved to: {output_path}")

        return output_path