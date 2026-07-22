"""
diarization/models.py

Data model for speaker diarization results.
"""
from dataclasses import dataclass


@dataclass
class SpeakerSegment:
    """
    A single speaker-attributed time span produced by diarization.

    Attributes:
        speaker_id: Diarization-assigned label (e.g. "SPEAKER_00").
        start: Start timestamp in seconds.
        end: End timestamp in seconds.
    """
    speaker_id: str
    start: float
    end: float
