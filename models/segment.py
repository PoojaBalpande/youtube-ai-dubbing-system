"""
Data model and serialization utilities for transcript segments and audio attributes.

Provides the TranscriptSegment and SegmentAudio dataclasses to capture timestamps,
original text, translated text, and segment-wise audio synchronization metadata.
"""

from dataclasses import dataclass, field
import json
from pathlib import Path


@dataclass
class SegmentAudio:
    """
    Data model representing audio generation and timing analysis for a segment.

    Attributes:
        file_path: The file path to the generated segment audio.
        expected_duration: Expected duration of the segment in seconds (end - start).
        actual_duration: Actual measured duration of the generated audio in seconds.
        timing_difference: Difference between actual and expected duration (actual - expected).
        sync_action: The synchronization decision made ("none", "pad", "speed").
    """
    file_path: str
    expected_duration: float
    actual_duration: float
    timing_difference: float
    sync_action: str


@dataclass
class TranscriptSegment:
    """
    Data model representing a single segment of transcribed audio.

    Attributes:
        start: Start timestamp of the segment in seconds.
        end: End timestamp of the segment in seconds.
        original_text: The transcribed source text.
        translated_text: The translated target text. Defaults to None.
        audio: Audio metadata and timing analysis parameters. Defaults to None.
        metadata: Extensible dictionary for storage of additional metadata
            (e.g., speaker ID, confidence scores, speaking rate) to support
            future synchronization and customization phases.
    """
    start: float
    end: float
    original_text: str
    translated_text: str | None = None
    audio: SegmentAudio | None = None
    metadata: dict = field(default_factory=dict)


def save_segments(segments: list[TranscriptSegment], output_path: Path) -> Path:
    """
    Serialize a list of TranscriptSegment objects to a JSON file.

    Args:
        segments: The list of TranscriptSegment objects to serialize.
        output_path: Target path where the JSON should be saved.

    Returns:
        The Path to the saved JSON file.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    serialized_data = []
    for segment in segments:
        segment_data = {
            "start": segment.start,
            "end": segment.end,
            "original": segment.original_text,
            "translated": segment.translated_text
        }

        if segment.audio is not None:
            segment_data["audio"] = {
                "file_path": str(segment.audio.file_path),
                "expected_duration": segment.audio.expected_duration,
                "actual_duration": segment.audio.actual_duration,
                "timing_difference": segment.audio.timing_difference,
                "sync_action": segment.audio.sync_action
            }

        serialized_data.append(segment_data)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(serialized_data, file, indent=2, ensure_ascii=False)

    return output_path
