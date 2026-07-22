"""
voice_cloning/xtts_cloner.py

Coqui XTTS-v2 backed voice cloning implementation. OpenVoice, CosyVoice,
and F5-TTS can be added as sibling classes registered in
voice_cloning_factory.py without touching this file or the TTS engine
call site.
"""
from pathlib import Path

from app.voice_cloning.base import BaseVoiceCloner
from app.utils.logger import get_logger

logger = get_logger(__name__)


class XTTSCloner(BaseVoiceCloner):
    """Zero-shot voice cloning using Coqui XTTS-v2."""

    def __init__(self) -> None:
        self._model = None

    def _load_model(self):
        if self._model is not None:
            return self._model

        try:
            from TTS.api import TTS
        except ImportError as error:
            raise RuntimeError(
                "Coqui TTS is not installed. Install it with 'pip install TTS' "
                "to enable XTTS-v2 voice cloning."
            ) from error

        logger.info("Loading XTTS-v2 model...")
        self._model = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
        logger.info("XTTS-v2 model loaded successfully.")
        return self._model

    def clone_voice(self, reference_audio_path: Path, text: str, output_path: Path) -> Path:
        if not reference_audio_path.exists():
            raise FileNotFoundError(f"Reference audio not found: {reference_audio_path}")

        model = self._load_model()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Cloning voice from {reference_audio_path.name} for text: '{text[:30]}...'")
        model.tts_to_file(
            text=text,
            speaker_wav=str(reference_audio_path),
            language="en",
            file_path=str(output_path),
        )
        return output_path
