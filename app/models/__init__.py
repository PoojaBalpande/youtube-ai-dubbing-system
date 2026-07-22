"""
Shared models package for YouTube AI Dubbing System.

Exposes core data classes and serialization functions.
"""

from app.models.segment import TranscriptSegment, SegmentAudio, save_segments

__all__ = [
    "TranscriptSegment",
    "SegmentAudio",
    "save_segments",
]
