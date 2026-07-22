"""
voice_cloning/base.py

Abstract interface for voice-cloning TTS backends (Milestone 7).
"""
from abc import ABC, abstractmethod
from pathlib import Path


class BaseVoiceCloner(ABC):
    """Common interface every voice-cloning backend must implement."""

    @abstractmethod
    def clone_voice(self, reference_audio_path: Path, text: str, output_path: Path) -> Path:
        """
        Synthesize `text` in the voice identity extracted from
        `reference_audio_path`, writing the result to `output_path`.

        Args:
            reference_audio_path: A short clean sample of the source
                speaker's voice, used to compute a speaker embedding.
            text: The target-language text to synthesize.
            output_path: Destination path for the generated audio.

        Returns:
            The path to the generated audio file.
        """
