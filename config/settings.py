from pathlib import Path
import os
from dotenv import load_dotenv

# Project root directory (two levels up from config/settings.py)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(PROJECT_ROOT / ".env")

# Logging Level
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Application directories
DOWNLOAD_DIR = PROJECT_ROOT / "downloads"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
TEMP_DIR = PROJECT_ROOT / "temp"
LOG_DIR = PROJECT_ROOT / "logs"

# YouTube Downloader Configuration
YTDLP_FORMAT = "bestvideo+bestaudio/best"
YTDLP_MERGE_OUTPUT_FORMAT = "mp4"

# Audio Extractor Configuration
AUDIO_EXTRACT_SAMPLE_RATE = 16000
AUDIO_EXTRACT_CHANNELS = 1

# Whisper Configuration
WHISPER_MODEL = "base"
DEVICE = "cpu"
TRANSCRIPTION_LANGUAGE = None      # Auto detect
BEAM_SIZE = 5
TEMPERATURE = 0.0

# Output File Paths
TRANSCRIPT_FILE = OUTPUT_DIR / "transcript.txt"
TRANSLATION_OUTPUT_FILE = OUTPUT_DIR / "translated_transcript.txt"
TRANSLATED_SEGMENTS_JSON = OUTPUT_DIR / "translated_segments.json"
DUBBED_VIDEO_OUTPUT = OUTPUT_DIR / "dubbed_video.mp4"

# Marian Translator Configuration
TRANSLATION_MODEL = "Helsinki-NLP/opus-mt-hi-en"
MAX_CHUNK_LENGTH = 8

# --- Translator Provider Selection ---
# Supported values: "marian", "groq"
TRANSLATOR_PROVIDER = os.getenv("TRANSLATION_PROVIDER", "groq")

# --- Context Window Configuration ---
CONTEXT_WINDOW = 3

# --- Translation Fallback Mechanism ---
ENABLE_TRANSLATION_FALLBACK = True
FALLBACK_TRANSLATOR = "marian"

# --- Groq Translator Configuration ---
GROQ_MODEL = os.getenv("GROQ_MODEL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_CHUNK_SIZE = 80
GROQ_TRANSLATION_PROMPT = """Translate the following text to {target_language} naturally.
The meaning, names, cities, organizations, brands, idioms, slang, conversational tone, and emotions must be preserved.
Do not translate literally. Keep punctuation natural.
Do not add any explanations, notes, or preambles. Return ONLY the translated text.

Source Text:
{text}

Translation:"""

# --- Timing & Sync Thresholds ---
SYNC_TOLERANCE_MS = 100
MAX_TTS_RATE_CHANGE = 15
ENABLE_RATE_ADJUSTMENT = True
ENABLE_SILENCE_PADDING = True

# --- Voice Management Selection ---
VOICE = os.getenv("VOICE", "en-US-GuyNeural")

# --- Audio Stitcher Configuration ---
OUTPUT_SAMPLE_RATE = 16000
OUTPUT_CHANNELS = 1

# --- Text-to-Speech Settings ---
TTS_RATE = "+0%"
TTS_RETRY_COUNT = 1

# --- Production FFmpeg Merger Configuration ---
VIDEO_CODEC = "copy"
AUDIO_CODEC = "aac"
FASTSTART = True


# --- Multi-language Dubbing Configuration (Milestone 3) ---
TARGET_LANGUAGE = os.getenv("TARGET_LANGUAGE", "en")

LANGUAGE_NAMES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
}

# --- Voice Pool Configuration (Milestones 3 & 5) ---
DEFAULT_MALE_VOICE = os.getenv("DEFAULT_MALE_VOICE", "en-US-GuyNeural")
DEFAULT_FEMALE_VOICE = os.getenv("DEFAULT_FEMALE_VOICE", "en-US-JennyNeural")

LANGUAGE_VOICE_MAP = {
    "en": {"male": "en-US-GuyNeural", "female": "en-US-JennyNeural"},
    "es": {"male": "es-ES-AlvaroNeural", "female": "es-ES-ElviraNeural"},
    "fr": {"male": "fr-FR-HenriNeural", "female": "fr-FR-DeniseNeural"},
    "de": {"male": "de-DE-ConradNeural", "female": "de-DE-KatjaNeural"},
}

# --- Speaker Diarization Configuration (Milestone 4) ---
ENABLE_DIARIZATION = os.getenv("ENABLE_DIARIZATION", "false").lower() == "true"
DIARIZATION_MODEL = os.getenv("DIARIZATION_MODEL", "pyannote/speaker-diarization-3.1")
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "")

# --- Emotion-aware Speech Configuration (Milestone 6) ---
ENABLE_EMOTION_TTS = os.getenv("ENABLE_EMOTION_TTS", "true").lower() == "true"

# --- Voice Cloning Configuration (Milestone 7) ---
ENABLE_VOICE_CLONING = os.getenv("ENABLE_VOICE_CLONING", "false").lower() == "true"
VOICE_CLONING_PROVIDER = os.getenv("VOICE_CLONING_PROVIDER", "xtts")
REFERENCE_AUDIO_DIR = TEMP_DIR / "reference_audio"
VOICE_PROVIDER = os.getenv("VOICE_PROVIDER", "edge").lower().strip()
VOICE_REFERENCE_SECONDS = float(os.getenv("VOICE_REFERENCE_SECONDS", "10.0"))
VOICE_CACHE = os.getenv("VOICE_CACHE", "true").lower() == "true"
MODEL_CACHE_DIR = os.getenv("MODEL_CACHE_DIR", "model_cache")

# --- Advanced Media Quality Configuration (Milestone 12) ---
ENABLE_LOUDNESS_NORMALIZATION = os.getenv("ENABLE_LOUDNESS_NORMALIZATION", "false").lower() == "true"
LOUDNESS_TARGET_LUFS = -16.0
