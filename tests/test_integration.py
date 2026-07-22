"""
test_integration.py

Integration tests for the XTTS voice cloning provider system.
"""
import unittest
from pathlib import Path
import os
from config import settings as config

# Programmatically configure environment for tests
os.environ["COQUI_TOS_AGREED"] = "1"
os.environ["TTS_HOME"] = os.path.abspath("model_cache")

from app.models.segment import TranscriptSegment
from app.tts.factory import get_tts_provider, reset_tts_provider
from app.voice_cloning.reference_extractor import ReferenceExtractor
from app.voice_cloning.embedding_cache import EmbeddingCache
from app.diarization.models import SpeakerSegment


class TestXTTSIntegration(unittest.TestCase):

    def setUp(self):
        reset_tts_provider()
        self.ref_audio = Path("temp/tts_wav/segment_0001.wav")
        if not self.ref_audio.exists():
            wavs = list(Path("temp").glob("**/*.wav"))
            if wavs:
                self.ref_audio = wavs[0]
        self.output_wav = Path("temp/test_output.wav")
        if self.output_wav.exists():
            self.output_wav.unlink()

    def test_factory_singleton(self):
        """Verify that factory reuse returns the exact same provider instance."""
        p1 = get_tts_provider("xtts")
        p2 = get_tts_provider("xtts")
        self.assertIs(p1, p2, "Factory must reuse singleton provider instance.")
        print("[OK] Factory singleton verified successfully.")

    def test_embedding_cache(self):
        """Verify that embedding cache computes latents once and reuses them."""
        p = get_tts_provider("xtts")
        cache = p.embedding_cache
        cache.clear()
        
        # First call: computes
        gpt1, emb1 = cache.get_latents("SPEAKER_TEST", self.ref_audio, p.tts_model)
        
        # Second call: fetches from cache
        gpt2, emb2 = cache.get_latents("SPEAKER_TEST", self.ref_audio, p.tts_model)
        
        self.assertIs(gpt1, gpt2)
        self.assertIs(emb1, emb2)
        print("[OK] Embedding cache verified successfully.")

    def test_synthesis_cloned_voice(self):
        """Verify that voice cloning synthesizes successfully and writes WAV output."""
        p = get_tts_provider("xtts")
        p.synthesize(
            text="Hello from the automated integration test for voice cloning.",
            output_path=self.output_wav,
            voice="en-US-GuyNeural",
            rate="+0%",
            pitch="+0Hz",
            reference_wav=self.ref_audio,
            language="en"
        )
        self.assertTrue(self.output_wav.exists())
        self.assertGreater(self.output_wav.stat().st_size, 1000)
        print("[OK] Synthesis of cloned voice verified successfully.")

    def test_automatic_fallback(self):
        """Verify that if XTTS synthesis fails (e.g. invalid wav path), Edge-TTS fallback is invoked."""
        from app.tts.tts_engine import SegmentTTS
        segment_tts = SegmentTTS()
        
        # Create a mock segment with non-existent reference audio to trigger failure
        seg = TranscriptSegment(
            start=0.0,
            end=2.0,
            original_text="Failed XTTS test segment.",
            translated_text="Failed XTTS test segment."
        )
        seg.metadata["speaker"] = "SPEAKER_BAD"
        seg.metadata["reference_audio"] = "non_existent_file.wav"
        
        # This call should catch the clone error, log it, fall back to Edge-TTS, and succeed!
        audio_meta = segment_tts.generate_segment(seg, index=999)
        self.assertTrue(Path(audio_meta.file_path).exists())
        self.assertGreater(Path(audio_meta.file_path).stat().st_size, 1000)
        print("[OK] Automatic fallback to Edge-TTS verified successfully.")


if __name__ == "__main__":
    unittest.main()
