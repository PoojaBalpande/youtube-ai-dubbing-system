"""
Segment-wise Text-to-Speech generation engine.

Leverages modular speech providers (Edge-TTS or XTTS-v2) to generate speech
audio files on a per-segment basis, integrates duration checks, and automatically
manages speedup rate changes.
"""

from pathlib import Path
from config import settings as config
from app.models.segment import TranscriptSegment, SegmentAudio
from app.timing.duration import calculate_expected_duration, calculate_actual_duration
from app.timing.sync import analyze_timing
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SegmentTTS:
    """
    Synthesizes speech segment-wise using configurable TTS providers.

    Determines deterministic filenames, measures expected vs. actual duration,
    and applies speedup adjustments if the generated segment exceeds its time.
    """

    def __init__(self) -> None:
        """Initialize and create temporary output directories and dynamically load providers."""
        self.default_rate_str: str = getattr(config, "TTS_RATE", "+0%")
        self.temp_dir: Path = Path(getattr(config, "TEMP_DIR", "temp")) / "tts"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.retry_count: int = getattr(config, "TTS_RETRY_COUNT", 1)

        # Initialize the active TTS provider from factory
        from app.tts.factory import get_tts_provider
        self.provider = get_tts_provider()

    def generate_segment(self, segment: TranscriptSegment, index: int) -> SegmentAudio:
        """
        Synthesize audio for a segment, measure duration, run sync analysis,
        and handle retry, provider fallback, or speedup adjustments.
        """
        filename = f"segment_{index:04d}.mp3"
        output_path = self.temp_dir / filename
        text = segment.translated_text or ""
        expected = calculate_expected_duration(segment.start, segment.end)

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

        from app.tts.voice_selector import select_voice
        voice = select_voice(segment)

        # Milestone 6: emotion-aware prosody
        emotion = {"label": "neutral", "rate": 0, "pitch": 0, "volume": 0}
        if getattr(config, "ENABLE_EMOTION_TTS", False):
            from app.emotion.emotion_detector import detect_emotion
            emotion = detect_emotion(text)
            segment.metadata["emotion"] = emotion["label"]

        pitch_str = f"+{emotion['pitch']}Hz" if emotion["pitch"] >= 0 else f"{emotion['pitch']}Hz"

        # Resolve active provider (interchangeable based on provider config or voice cloning enable)
        active_provider = self.provider
        is_cloning_enabled = getattr(config, "ENABLE_VOICE_CLONING", False) or getattr(config, "VOICE_PROVIDER", "edge") == "xtts"
        
        if is_cloning_enabled and segment.metadata.get("reference_audio"):
            # Ensure active provider is XTTS
            if active_provider.__class__.__name__ != "XTTSProvider":
                from app.tts.factory import get_tts_provider
                active_provider = get_tts_provider("xtts")

        base_val = 0
        if self.default_rate_str.endswith("%"):
            try:
                base_val = int(self.default_rate_str.rstrip("%").lstrip("+"))
            except ValueError:
                pass
        combined_val = base_val + emotion["rate"]
        rate_str = f"+{combined_val}%" if combined_val >= 0 else f"{combined_val}%"

        success = False
        for attempt in range(self.retry_count + 1):
            try:
                if attempt == 0:
                    logger.info(f"Generating segment {index} using provider {active_provider.__class__.__name__}... Text: '{text[:30]}...'")
                else:
                    logger.warning(f"Synthesis attempt {attempt} failed for segment {index}. Retrying (attempt {attempt + 1}/{self.retry_count + 1})...")
                
                reference_audio = segment.metadata.get("reference_audio")
                active_provider.synthesize(
                    text=text,
                    output_path=output_path,
                    voice=voice,
                    rate=rate_str,
                    pitch=pitch_str,
                    reference_wav=Path(reference_audio) if reference_audio else None,
                    language=getattr(config, "TARGET_LANGUAGE", "en"),
                    segment_index=index
                )
                success = True
                break
            except Exception as error:
                logger.error(f"Synthesis error on attempt {attempt + 1} with provider {active_provider.__class__.__name__}: {error}")
                
                # Check for automatic fallback if the failed provider was XTTS
                if active_provider.__class__.__name__ == "XTTSProvider":
                    logger.warning(f"XTTS voice cloning failed for segment {index}. Automatically falling back to Edge-TTS. Error: {error}")
                    try:
                        from app.tts.edge_provider import EdgeTTSProvider
                        fallback_provider = EdgeTTSProvider()
                        fallback_provider.synthesize(
                            text=text,
                            output_path=output_path,
                            voice=voice,
                            rate=rate_str,
                            pitch=pitch_str,
                            reference_wav=None,
                            language=getattr(config, "TARGET_LANGUAGE", "en"),
                            segment_index=index
                        )
                        active_provider = fallback_provider
                        success = True
                        break
                    except Exception as fallback_error:
                        logger.error(f"Automatic fallback to Edge-TTS also failed for segment {index}: {fallback_error}")

        if not success:
            logger.error(f"All synthesis attempts ({self.retry_count + 1}) failed for segment {index}.")
            output_path.touch()
            return SegmentAudio(
                file_path=str(output_path),
                expected_duration=expected,
                actual_duration=0.0,
                timing_difference=-expected,
                sync_action="none"
            )

        actual = calculate_actual_duration(output_path)
        analysis = analyze_timing(expected, actual)

        if analysis["action"] == "speed" and analysis["value"] > 0:
            speedup = analysis["value"]
            target_val = combined_val + int(round(speedup))
            adjusted_rate_str = f"+{target_val}%" if target_val >= 0 else f"{target_val}%"

            logger.info(
                f"Segment {index} TTS is longer than expected (diff: +{analysis['difference']:.2f}s). "
                f"Regenerating audio with speedup rate: {adjusted_rate_str}"
            )

            try:
                # For speedup adjustments, we always use standard Edge-TTS/cloning to adjust output speed
                active_provider.synthesize(
                    text=text,
                    output_path=output_path,
                    voice=voice,
                    rate=adjusted_rate_str,
                    pitch=pitch_str,
                    reference_wav=Path(segment.metadata["reference_audio"]) if is_cloning_enabled and segment.metadata.get("reference_audio") else None,
                    language=getattr(config, "TARGET_LANGUAGE", "en"),
                    segment_index=index
                )
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
