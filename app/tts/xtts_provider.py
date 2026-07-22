"""
tts/xtts_provider.py

XTTS-v2 based speech synthesis provider. Loads the model once during pipeline
startup and leverages the embedding cache to perform fast voice cloning inference.
"""
import os
from pathlib import Path
from config import settings as config
from app.tts.provider import BaseTTSProvider
from app.voice_cloning.embedding_cache import EmbeddingCache
from app.utils.logger import get_logger

logger = get_logger(__name__)


class XTTSProvider(BaseTTSProvider):
    """Provides speech synthesis and voice cloning using Coqui XTTS-v2."""

    def __init__(self) -> None:
        """Initialize the XTTS provider and load the model once."""
        # Programmatically configure Hugging Face model cache directory and agree to TOS
        os.environ["TTS_HOME"] = os.path.abspath(getattr(config, "MODEL_CACHE_DIR", "model_cache"))
        os.environ["COQUI_TOS_AGREED"] = "1"

        # ── Work around SpeechBrain lazy-module conflict ──────────────
        # When pyannote.audio loads SpeechBrain 1.x, it registers several
        # lazy placeholder modules in sys.modules (for k2, flair, spacy,
        # wordemb, transducer_loss, etc.).  Later, when Coqui TTS imports
        # librosa, librosa calls inspect.stack() → inspect.getmodule()
        # which iterates sys.modules and triggers hasattr(module, '__file__')
        # on every entry.  Each unloaded SpeechBrain LazyModule intercepts
        # __getattr__, tries to actually import its optional dependency
        # (k2, flair, etc.), and crashes the process.
        #
        # Fix: remove ALL SpeechBrain LazyModule / DeprecatedModuleRedirect
        # instances from sys.modules before TTS is imported.  We identify
        # them using type(mod).__name__ instead of isinstance() or getattr()
        # because ANY attribute access on a LazyModule triggers __getattr__
        # which forces the lazy import and crashes.
        #
        # This is safe because pyannote has already finished its setup and
        # holds direct references to the real modules it needs.
        import sys
        _sb_lazy_types = frozenset({'LazyModule', 'DeprecatedModuleRedirect'})
        _poisoned = [
            name for name, mod in list(sys.modules.items())
            if 'speechbrain' in name and type(mod).__name__ in _sb_lazy_types
        ]
        for name in _poisoned:
            del sys.modules[name]
            logger.debug(f"Removed SpeechBrain lazy placeholder: {name}")

        try:
            from TTS.api import TTS
        except ImportError as error:
            raise RuntimeError(
                f"Failed to import Coqui TTS: {error}. "
                f"Ensure coqui-tts is installed and no conflicting modules "
                f"are polluting sys.modules."
            ) from error

        model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
        
        # Check GPU availability
        import torch
        self.use_gpu = torch.cuda.is_available()
        logger.info(f"Loading XTTS-v2 model: '{model_name}'. CUDA Acceleration: {self.use_gpu}")
        
        self.tts = TTS(model_name, gpu=self.use_gpu)
        self.tts_model = self.tts.synthesizer.tts_model
        logger.info("XTTS-v2 model loaded successfully.")

        # Initialize the embedding cache
        self.embedding_cache = EmbeddingCache()

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
        """Synthesizes speech using the cloned voice of the target speaker."""
        if not reference_wav:
            raise ValueError(f"XTTS requires a reference WAV file. Missing for segment {segment_index}.")

        if not reference_wav.exists():
            raise FileNotFoundError(f"Reference WAV file not found: {reference_wav}")

        # Derive speaker ID from the reference audio filename (e.g. "ref_SPEAKER_01" -> "SPEAKER_01")
        speaker_id = reference_wav.stem.replace("ref_", "")
        
        # Retrieve or compute the conditioning latents for the speaker
        gpt_cond_latent, speaker_embedding = self.embedding_cache.get_latents(
            speaker_id=speaker_id,
            reference_wav_path=reference_wav,
            tts_model=self.tts_model
        )

        logger.info(f"Synthesizing segment {segment_index} with cloned voice of speaker {speaker_id}...")
        
        # Clean language code (XTTS expects short language code like "en", "es", etc.)
        short_lang = language.split("-")[0]
        
        # Perform direct fast model inference using cached latents
        outputs = self.tts_model.inference(
            text=text,
            language=short_lang,
            gpt_cond_latent=gpt_cond_latent,
            speaker_embedding=speaker_embedding
        )
        
        # Save output using synthesizer save utility
        wav = outputs["wav"]
        self.tts.synthesizer.save_wav(wav, str(output_path))
        logger.info(f"Cloned audio saved successfully to {output_path.name}")
