"""
diarization/speaker_detector.py

Speaker diarization via pyannote.audio, with assignment of speaker
labels onto existing TranscriptSegment objects by timestamp overlap.
Purely additive: writes only into TranscriptSegment.metadata["speaker"].
"""
from pathlib import Path

from config import settings as config
from app.diarization.models import SpeakerSegment
from app.models.segment import TranscriptSegment
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SpeakerDetector:
    """Wraps a pyannote.audio speaker-diarization pipeline."""

    def __init__(self) -> None:
        self.model_name: str = getattr(config, "DIARIZATION_MODEL", "pyannote/speaker-diarization-3.1")
        self.auth_token: str = getattr(config, "HUGGINGFACE_TOKEN", "")
        self._pipeline = None

    def _load_pipeline(self):
        if self._pipeline is not None:
            return self._pipeline

        try:
            from pyannote.audio import Pipeline
        except ImportError as error:
            raise RuntimeError(
                "pyannote.audio is not installed. Install it with "
                "'pip install pyannote.audio' to enable speaker diarization."
            ) from error

        logger.info(f"Loading diarization model: {self.model_name}")
        try:
            self._pipeline = Pipeline.from_pretrained(
                self.model_name,
                use_auth_token=self.auth_token or None,
            )
        except Exception:
            logger.exception("Failed to load diarization pipeline.")
            raise

        logger.info("Diarization model loaded successfully.")
        return self._pipeline

    def detect(self, audio_path: Path) -> list[SpeakerSegment]:
        """
        Run diarization on an audio file and return speaker-labeled spans.

        Args:
            audio_path: Path to the extracted mono WAV audio.

        Returns:
            A list of SpeakerSegment objects ordered by start time.
        """
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        pipeline = self._load_pipeline()

        logger.info(f"Running speaker diarization on: {audio_path.name}")
        diarization = pipeline(str(audio_path))

        speaker_segments = [
            SpeakerSegment(speaker_id=speaker, start=float(turn.start), end=float(turn.end))
            for turn, _, speaker in diarization.itertracks(yield_label=True)
        ]

        speaker_segments.sort(key=lambda s: s.start)
        logger.info(f"Diarization detected {len(set(s.speaker_id for s in speaker_segments))} speaker(s).")
        return speaker_segments

    def assign_speakers_to_segments(
        self,
        transcript_segments: list[TranscriptSegment],
        speaker_segments: list[SpeakerSegment],
    ) -> None:
        """
        Attach the best-overlapping speaker label to each transcript
        segment's metadata, in place.

        Args:
            transcript_segments: Segments produced by WhisperEngine.
            speaker_segments: Segments produced by detect().
        """
        if not speaker_segments:
            logger.warning("No speaker segments available; skipping speaker assignment.")
            return

        for segment in transcript_segments:
            best_speaker = None
            best_overlap = 0.0

            for spk in speaker_segments:
                overlap = min(segment.end, spk.end) - max(segment.start, spk.start)
                if overlap > best_overlap:
                    best_overlap = overlap
                    best_speaker = spk.speaker_id

            segment.metadata["speaker"] = best_speaker or "SPEAKER_00"
