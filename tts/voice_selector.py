"""
Voice selector module for Text-to-Speech engine.

Responsible for selecting the appropriate voice based on segment properties.
Isolates voice selection logic from the core synthesis logic, allowing future
extension (e.g., speaker gender/emotion alignment) without modifying TTS engine code.
"""

import config
from models.segment import TranscriptSegment


def select_voice(segment: TranscriptSegment) -> str:
    """
    Select the appropriate Edge-TTS voice for a given segment.

    Currently returns the standard configured voice from config.py.
    Future phases can inspect ``segment.metadata`` (e.g. speaker ID)
    to select speaker-specific or emotion-aware voices.

    Args:
        segment: The TranscriptSegment to analyze.

    Returns:
        The string name of the selected Edge-TTS voice.
    """
    # Return configured voice from config, defaulting to standard guy neural voice
    return getattr(config, "VOICE", "en-US-GuyNeural")
