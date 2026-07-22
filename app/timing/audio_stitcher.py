"""
Audio timeline stitcher module.

Responsible for taking a list of TranscriptSegments, retrieving their segment-level
generated audio, normalising formats via conversion to PCM WAV, constructing a
fully synchronized timeline with silence padding, and exporting a single WAV.
"""

import wave
from pathlib import Path

from config import settings as config
from app.audio.converter import convert_mp3_to_wav
from app.models.segment import TranscriptSegment
from app.utils.logger import get_logger


logger = get_logger(__name__)


class AudioStitcher:
    """
    Timeline compiler that stitches normalized audio files into a single WAV track,
    automatically aligning segment positions to match original timestamps and
    padding decisions without re-encoding audio repeatedly.
    """

    def __init__(self) -> None:
        """Initialize the audio stitcher with configurable output formats."""
        self.sample_rate: int = getattr(config, "OUTPUT_SAMPLE_RATE", 16000)
        self.channels: int = getattr(config, "OUTPUT_CHANNELS", 1)
        self.bytes_per_sample: int = 2  # 16-bit PCM (pcm_s16le)
        self.temp_wav_dir: Path = Path(getattr(config, "TEMP_DIR", "temp")) / "tts_wav"
        self.temp_wav_dir.mkdir(parents=True, exist_ok=True)

    def stitch(self, segments: list[TranscriptSegment], output_wav_path: Path) -> Path:
        """
        Stitch segments together into a single synchronized PCM WAV file.

        Args:
            segments: Ordered list of TranscriptSegment objects.
            output_wav_path: The target export path for the final stitched WAV.

        Returns:
            The Path to the final stitched WAV file.
        """
        logger.info("Starting audio stitching and timeline compilation...")
        output_wav_path.parent.mkdir(parents=True, exist_ok=True)

        # Ensure segments are sorted chronologically
        sorted_segments = sorted(segments, key=lambda s: s.start)

        with wave.open(str(output_wav_path), "wb") as out_wav:
            out_wav.setnchannels(self.channels)
            out_wav.setsampwidth(self.bytes_per_sample)
            out_wav.setframerate(self.sample_rate)

            current_frame = 0

            for index, segment in enumerate(sorted_segments, start=1):
                # Calculate the exact target start frame on the timeline
                target_start_frame = int(round(segment.start * self.sample_rate))

                # 1. Fill silence gap if target start is ahead of the current timeline head
                if target_start_frame > current_frame:
                    gap_frames = target_start_frame - current_frame
                    logger.info(f"Inserting {gap_frames / self.sample_rate:.2f}s silence gap before segment {index}.")
                    
                    # 16-bit PCM silence is filled with null bytes (0x00)
                    silence_data = b"\x00" * (gap_frames * self.channels * self.bytes_per_sample)
                    out_wav.writeframes(silence_data)
                    current_frame = target_start_frame

                # 2. Check segment audio availability
                if not segment.audio or not segment.audio.file_path:
                    logger.warning(
                        f"Segment {index} audio details missing. "
                        f"Inserting expected duration silence ({segment.end - segment.start:.2f}s)."
                    )
                    expected_dur = segment.end - segment.start
                    missing_frames = int(round(expected_dur * self.sample_rate))
                    silence_data = b"\x00" * (missing_frames * self.channels * self.bytes_per_sample)
                    out_wav.writeframes(silence_data)
                    current_frame += missing_frames
                    continue

                mp3_path = Path(segment.audio.file_path)
                wav_filename = f"segment_{index:04d}.wav"
                wav_path = self.temp_wav_dir / wav_filename

                # 3. Convert segment audio MP3 to normalized PCM WAV
                try:
                    if not mp3_path.exists():
                        logger.warning(
                            f"Segment {index} audio file not found: {mp3_path}. "
                            f"Inserting expected duration silence."
                        )
                        expected_dur = segment.end - segment.start
                        missing_frames = int(round(expected_dur * self.sample_rate))
                        silence_data = b"\x00" * (missing_frames * self.channels * self.bytes_per_sample)
                        out_wav.writeframes(silence_data)
                        current_frame += missing_frames
                        continue

                    # Execute normalization conversion
                    convert_mp3_to_wav(mp3_path, wav_path, self.sample_rate, self.channels)
                except Exception as error:
                    logger.error(
                        f"Failed to convert segment {index} audio: {error}. "
                        f"Inserting expected duration silence."
                    )
                    expected_dur = segment.end - segment.start
                    missing_frames = int(round(expected_dur * self.sample_rate))
                    silence_data = b"\x00" * (missing_frames * self.channels * self.bytes_per_sample)
                    out_wav.writeframes(silence_data)
                    current_frame += missing_frames
                    continue

                # 4. Read the frames from normalized PCM WAV segment and write to output
                try:
                    with wave.open(str(wav_path), "rb") as in_wav:
                        # Verify properties
                        if (in_wav.getnchannels() != self.channels or
                            in_wav.getsampwidth() != self.bytes_per_sample or
                            in_wav.getframerate() != self.sample_rate):
                            raise ValueError("WAV normalization parameters mismatch.")

                        num_frames = in_wav.getnframes()
                        frame_data = in_wav.readframes(num_frames)

                        logger.info(f"Appending segment {index} audio ({num_frames / self.sample_rate:.2f}s).")
                        out_wav.writeframes(frame_data)
                        current_frame += num_frames
                except Exception as error:
                    logger.error(
                        f"Failed to read segment {index} WAV: {error}. "
                        f"Inserting expected duration silence."
                    )
                    expected_dur = segment.end - segment.start
                    missing_frames = int(round(expected_dur * self.sample_rate))
                    silence_data = b"\x00" * (missing_frames * self.channels * self.bytes_per_sample)
                    out_wav.writeframes(silence_data)
                    current_frame += missing_frames
                    continue

        logger.info(f"Stitching completed successfully. Final WAV saved to: {output_wav_path}")
        return output_wav_path
