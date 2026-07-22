from config import settings as config
from app.models.segment import TranscriptSegment

# Speaker -> voice assignment cache (Milestone 5), persists for the run
_speaker_voice_cache: dict[str, str] = {}


def _resolve_language_voices() -> tuple[str, str]:
    target_language = getattr(config, "TARGET_LANGUAGE", "en")
    voice_map = getattr(config, "LANGUAGE_VOICE_MAP", {})
    pair = voice_map.get(target_language)
    if pair:
        return pair["male"], pair["female"]
    return (
        getattr(config, "DEFAULT_MALE_VOICE", "en-US-GuyNeural"),
        getattr(config, "DEFAULT_FEMALE_VOICE", "en-US-JennyNeural"),
    )


def select_voice(segment: TranscriptSegment) -> str:
    """
    Select the appropriate Edge-TTS voice for a given segment.

    If the segment carries a diarized speaker ID (Milestone 4 metadata),
    it is deterministically assigned a male/female voice from the
    target-language pool, alternating per new speaker and cached for
    consistency across the video. Without speaker metadata, the single
    target-language voice is returned, preserving prior behavior.
    """
    speaker_id = segment.metadata.get("speaker")
    male_voice, female_voice = _resolve_language_voices()

    if not speaker_id:
        return male_voice

    if speaker_id not in _speaker_voice_cache:
        is_even = len(_speaker_voice_cache) % 2 == 0
        _speaker_voice_cache[speaker_id] = male_voice if is_even else female_voice

    return _speaker_voice_cache[speaker_id]
