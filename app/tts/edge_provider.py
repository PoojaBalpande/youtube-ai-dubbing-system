"""
tts/edge_provider.py

Edge-TTS based speech synthesis provider.
"""
import asyncio
from pathlib import Path
import edge_tts
from app.tts.provider import BaseTTSProvider
from app.utils.logger import get_logger

logger = get_logger(__name__)


class EdgeTTSProvider(BaseTTSProvider):
    """Provides speech synthesis using Microsoft Edge TTS."""

    async def _generate_speech(self, text: str, output_path: Path, rate: str, voice: str, pitch: str) -> None:
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=rate,
            pitch=pitch,
        )
        await communicate.save(str(output_path))

    def synthesize(
        self,
        text: str,
        output_path: Path,
        voice: str,
        rate: str,
        pitch: str,
        reference_wav: Path | None = None,
        language: str = "en",
        segment_index: int = 1
    ) -> None:
        """Invokes Edge-TTS Communicate synchronously."""
        logger.info(f"Synthesizing segment {segment_index} using EdgeTTSProvider (voice={voice}, rate={rate}, pitch={pitch})...")
        asyncio.run(self._generate_speech(text, output_path, rate, voice, pitch))
