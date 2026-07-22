"""
tts/provider.py

Declares the BaseTTSProvider abstract base class representing the contract
for all text-to-speech providers.
"""
from abc import ABC, abstractmethod
from pathlib import Path


class BaseTTSProvider(ABC):
    """Abstract interface defining the contract for all TTS backend providers."""

    @abstractmethod
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
        """
        Synthesize text to speech and save it to output_path.

        Args:
            text: The translated text to synthesize.
            output_path: Target Path to write the output audio file.
            voice: Default target voice identifier (used by Edge-TTS).
            rate: Speedup or rate adjustment string (e.g. "+5%").
            pitch: Pitch modulation offset string (e.g. "+3Hz").
            reference_wav: Optional reference audio path for voice cloning.
            language: Target language code (e.g. "en").
            segment_index: The segment index number for logging.
        """
        pass
