"""
voice_cloning/embedding_cache.py

In-memory cache for speaker conditioning latents (embeddings) to avoid re-computation.
"""
from pathlib import Path
from app.utils.logger import get_logger

logger = get_logger(__name__)


class EmbeddingCache:
    """Caches speaker latents (gpt_cond_latent and speaker_embedding) in memory."""

    def __init__(self) -> None:
        # Maps speaker_id -> tuple(gpt_cond_latent, speaker_embedding)
        self._cache: dict[str, tuple] = {}

    def get_latents(self, speaker_id: str, reference_wav_path: Path, tts_model) -> tuple:
        """
        Retrieve or compute speaker conditioning latents for the given speaker.

        Args:
            speaker_id: Unique identifier for the speaker (e.g. "SPEAKER_00").
            reference_wav_path: Path to the clean reference WAV file.
            tts_model: The loaded XTTS model instance.

        Returns:
            A tuple of (gpt_cond_latent, speaker_embedding) tensors.
        """
        if speaker_id in self._cache:
            logger.info(f"Reusing cached speaker embedding for speaker: {speaker_id}")
            return self._cache[speaker_id]

        if not reference_wav_path.exists():
            raise FileNotFoundError(f"Reference WAV file does not exist: {reference_wav_path}")

        logger.info(f"Computing speaker embedding for speaker: {speaker_id} from {reference_wav_path.name}...")
        
        # Extract latents
        # get_conditioning_latents returns a tuple/list: (gpt_cond_latent, speaker_embedding)
        latents = tts_model.get_conditioning_latents(str(reference_wav_path))
        gpt_cond_latent, speaker_embedding = latents[0], latents[1]

        # Cache the extracted tensors
        self._cache[speaker_id] = (gpt_cond_latent, speaker_embedding)
        logger.info(f"Cached speaker embedding for speaker: {speaker_id}")
        
        return gpt_cond_latent, speaker_embedding

    def clear(self) -> None:
        """Clear the in-memory cache."""
        self._cache.clear()
        logger.info("Speaker embedding cache cleared.")
