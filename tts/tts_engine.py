"""
Segment-wise Text-to-Speech generation engine.

Leverages Microsoft Edge TTS to generate speech audio files on a per-segment
basis, integrates duration checks, and automatically manages speedup rate changes.
"""

import asyncio
from pathlib import Path
import edge_tts

import config
from models.segment import TranscriptSegment, SegmentAudio
from timing.duration import calculate_expected_duration, calculate_actual_duration
from timing.sync import analyze_timing
from utils.logger import get_logger


logger = get_logger(__name__)


class SegmentTTS:
    """
    Synthesizes speech segment-wise using Edge-TTS.

    Determines deterministic filenames, measures expected vs. actual duration,
    and applies speedup adjustments if the generated segment exceeds its time.
    """

    def __init__(self) -> None:
        """Initialize and create temporary output directories."""
        self.voice: str = getattr(config, "TTS_VOICE", "en-US-AriaNeural")
        self.default_rate_str: str = getattr(config, "TTS_RATE", "+0%")
        self.temp_dir: Path = Path(getattr(config, "TEMP_DIR", "temp")) / "tts"
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    async def _generate_speech(self, text: str, output_path: Path, rate: str, voice: str) -> None:
        """
        Asynchronously invoke Edge-TTS Communicate to generate audio file.

        Args:
            text: The text to convert to speech.
            output_path: Target path to save the generated audio.
            rate: The speech rate change parameter (e.g. "+10%", "-5%").
            voice: The Edge-TTS voice string name.
        """
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=rate
        )
        await communicate.save(str(output_path))

    def _run_synthesis(self, text: str, output_path: Path, rate: str, voice: str) -> None:
        """Helper to run the async synthesize operation synchronously."""
        asyncio.run(self._generate_speech(text, output_path, rate, voice))

    def generate_segment(self, segment: TranscriptSegment, index: int) -> SegmentAudio:
        """
        Synthesize audio for a segment, measure duration, run sync analysis,
        and handle retry or speedup adjustments.

        Args:
            segment: The TranscriptSegment containing translated text.
            index: Sequential segment index (for deterministic naming).

        Returns:
            A SegmentAudio object containing duration measurements and sync action.
        """
        filename = f"segment_{index:04d}.mp3"
        output_path = self.temp_dir / filename
        text = segment.translated_text or ""
        expected = calculate_expected_duration(segment.start, segment.end)

        # Handle empty translation text (generate silence or empty path)
        if not text.strip():
            logger.info(f"Segment {index} translation is empty. Creating empty file.")
            output_path.touch()
            return SegmentAudio(
                file_path=str(output_path),
                expected_duration=expected,
                actual_duration=0.0,
                timing_difference=-expected,
                sync_action="pad"
            )

        rate_str = self.default_rate_str

        # Select voice dynamically
        from tts.voice_selector import select_voice
        voice = select_voice(segment)

        # Primary generation try-except (with retry)
        try:
            logger.info(f"Generating segment {index} using voice {voice}... Text: '{text[:30]}...'")
            self._run_synthesis(text, output_path, rate_str, voice)
        except Exception as error:
            logger.warning(f"Synthesis failed for segment {index}: {error}. Retrying once...")
            try:
                self._run_synthesis(text, output_path, rate_str, voice)
            except Exception as retry_error:
                logger.error(f"Retry synthesis failed for segment {index}: {retry_error}")
                # Create empty file so stitching/subsequent phases don't fail, and return graceful metadata
                output_path.touch()
                return SegmentAudio(
                    file_path=str(output_path),
                    expected_duration=expected,
                    actual_duration=0.0,
                    timing_difference=-expected,
                    sync_action="none"
                )

        # Measure actual duration of generated file
        actual = calculate_actual_duration(output_path)

        # Analyze timing difference
        analysis = analyze_timing(expected, actual)

        # If actual audio is longer, apply speech speedup rate adjustment
        if analysis["action"] == "speed" and analysis["value"] > 0:
            speedup = analysis["value"]
            
            # Parse the default base rate (e.g. "+5%") and calculate target speed rate
            base_val = 0
            if self.default_rate_str.endswith("%"):
                try:
                    base_val = int(self.default_rate_str.rstrip("%"))
                except ValueError:
                    pass

            target_val = base_val + int(round(speedup))
            adjusted_rate_str = f"+{target_val}%" if target_val >= 0 else f"{target_val}%"

            logger.info(
                f"Segment {index} TTS is longer than expected (diff: +{analysis['difference']:.2f}s). "
                f"Regenerating audio with speedup rate: {adjusted_rate_str}"
            )

            try:
                self._run_synthesis(text, output_path, adjusted_rate_str, voice)
                # Remeasure and update timing parameters after rate adjustment regeneration
                actual = calculate_actual_duration(output_path)
                analysis = analyze_timing(expected, actual)
            except Exception as regen_error:
                logger.error(f"Regeneration with rate adjustment failed for segment {index}: {regen_error}")

        diff = actual - expected
        logger.info(
            f"Segment {index} generated successfully: "
            f"Expected: {expected:.2f}s, Actual: {actual:.2f}s, Diff: {diff:+.2f}s (Action: {analysis['action']})"
        )

        return SegmentAudio(
            file_path=str(output_path),
            expected_duration=expected,
            actual_duration=actual,
            timing_difference=diff,
            sync_action=analysis["action"]
        )
