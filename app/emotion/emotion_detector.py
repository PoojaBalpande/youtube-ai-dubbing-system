"""
emotion/emotion_detector.py

Lightweight, dependency-free emotion classification for TTS prosody
adjustment, using lexical and punctuation cues rather than a heavy
model. A transformer-based classifier can later replace detect_emotion's
internals without changing the call site.
"""
import re

EMOTION_PROFILES = {
    "excited":  {"rate": 15,  "pitch": 8,  "volume": 10},
    "happy":    {"rate": 8,   "pitch": 5,  "volume": 5},
    "angry":    {"rate": 10,  "pitch": -3, "volume": 15},
    "sad":      {"rate": -10, "pitch": -6, "volume": -5},
    "question": {"rate": 0,   "pitch": 6,  "volume": 0},
    "neutral":  {"rate": 0,   "pitch": 0,  "volume": 0},
}

_HAPPY_WORDS = {"great", "wonderful", "amazing", "love", "happy", "glad", "excellent", "fantastic"}
_SAD_WORDS = {"sad", "sorry", "unfortunately", "miss", "lost", "cry", "regret", "hurt"}
_ANGRY_WORDS = {"angry", "furious", "hate", "terrible", "worst", "stupid", "annoyed"}


def detect_emotion(text: str) -> dict:
    """
    Classify the dominant emotion of a text segment.

    Args:
        text: The (translated) segment text to analyze.

    Returns:
        A dict with "label" and prosody adjustment "rate"/"pitch"/"volume"
        deltas consumed by the TTS engine.
    """
    if not text or not text.strip():
        return {"label": "neutral", **EMOTION_PROFILES["neutral"]}

    stripped = text.strip()
    lowered = stripped.lower()
    words = set(re.findall(r"[a-zA-Z']+", lowered))

    if stripped.endswith("?"):
        label = "question"
    elif stripped.count("!") >= 1 and (words & _HAPPY_WORDS or stripped.isupper()):
        label = "excited"
    elif words & _ANGRY_WORDS:
        label = "angry"
    elif words & _SAD_WORDS:
        label = "sad"
    elif words & _HAPPY_WORDS:
        label = "happy"
    else:
        label = "neutral"

    return {"label": label, **EMOTION_PROFILES[label]}
