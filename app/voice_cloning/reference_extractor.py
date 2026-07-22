"""
voice_cloning/reference_extractor.py

Extracts clean reference WAV files for diarized speakers from the original audio.
"""
from pathlib import Path
import subprocess
from config import settings as config
from app.utils.logger import get_logger
from app.diarization.models import SpeakerSegment

logger = get_logger(__name__)


class ReferenceExtractor:
    """Extracts reference audio clips for speakers using diarization segments."""

    def __init__(self) -> None:
        self.output_dir: Path = getattr(config, "REFERENCE_AUDIO_DIR", Path("temp/reference_audio"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.min_length: float = float(getattr(config, "VOICE_REFERENCE_SECONDS", 10.0))

    def extract_speakers_references(self, audio_path: Path, speaker_segments: list[SpeakerSegment]) -> dict[str, Path]:
        """
        For each unique speaker, find the longest contiguous segment, slice it from the original audio,
        and save it as a WAV reference file.

        Args:
            audio_path: Path to the original full audio WAV file.
            speaker_segments: List of SpeakerSegment objects from app.diarization.

        Returns:
            A dictionary mapping speaker_id to the extracted Path.
        """
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        if not speaker_segments:
            logger.warning("No speaker segments provided for reference extraction.")
            return {}

        # Group segments by speaker ID
        speaker_groups: dict[str, list[SpeakerSegment]] = {}
        for seg in speaker_segments:
            speaker_groups.setdefault(seg.speaker_id, []).append(seg)

        references: dict[str, Path] = {}

        for speaker_id, segments in speaker_groups.items():
            # Find the longest segment
            longest_seg = max(segments, key=lambda s: s.end - s.start)
            duration = longest_seg.end - longest_seg.start
            logger.info(f"Speaker {speaker_id}: Longest segment is {duration:.2f}s (from {longest_seg.start:.2f} to {longest_seg.end:.2f})")

            # Extract the segment
            out_name = f"ref_{speaker_id}.wav"
            out_path = self.output_dir / out_name

            # Using ffmpeg to slice the WAV
            cmd = [
                "ffmpeg", "-y",
                "-ss", f"{longest_seg.start:.4f}",
                "-to", f"{longest_seg.end:.4f}",
                "-i", str(audio_path),
                str(out_path)
            ]
            
            logger.info(f"Extracting reference for {speaker_id} to {out_path} using FFmpeg...")
            try:
                subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                references[speaker_id] = out_path
                logger.info(f"Successfully extracted reference for {speaker_id} ({duration:.2f}s).")
            except subprocess.CalledProcessError as error:
                logger.error(f"Failed to extract reference for {speaker_id}: {error.stderr.decode(errors='ignore')}")
                
        return references
