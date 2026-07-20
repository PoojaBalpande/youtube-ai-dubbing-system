from pathlib import Path
import os
from dotenv import load_dotenv

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent

# Load environment variables
load_dotenv(PROJECT_ROOT / ".env")

# Application directories
DOWNLOAD_DIR = PROJECT_ROOT / "downloads"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
TEMP_DIR = PROJECT_ROOT / "temp"
LOG_DIR = PROJECT_ROOT / "logs"


# Create directories automatically
for directory in (
    DOWNLOAD_DIR,
    OUTPUT_DIR,
    TEMP_DIR,
    LOG_DIR,
):
    directory.mkdir(parents=True, exist_ok=True)
    
# Whisper Configuration
WHISPER_MODEL = "base"

# Device Configuration
DEVICE = "cpu"

# Transcription Configuration
TRANSCRIPTION_LANGUAGE = None      # Auto detect
BEAM_SIZE = 5
TEMPERATURE = 0.0

# Output
TRANSCRIPT_FILE = OUTPUT_DIR / "transcript.txt"

TRANSLATION_MODEL = "Helsinki-NLP/opus-mt-hi-en"

MAX_CHUNK_LENGTH = 8

TRANSLATION_OUTPUT_FILE = OUTPUT_DIR / "translated_transcript.txt"
TRANSLATED_SEGMENTS_JSON = OUTPUT_DIR / "translated_segments.json"

# --- Translator Provider Selection ---
# Supported values: "marian", "groq", "indic"
TRANSLATOR_PROVIDER = os.getenv("TRANSLATION_PROVIDER", "groq")

# --- Context Window Configuration ---
CONTEXT_WINDOW = 3

# --- Translation Fallback Mechanism ---
ENABLE_TRANSLATION_FALLBACK = True
FALLBACK_TRANSLATOR = "marian"

# --- Groq Translator Configuration ---
GROQ_MODEL = os.getenv("GROQ_MODEL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_TRANSLATION_PROMPT = """Translate the following text to English naturally.
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
VOICE = "en-US-GuyNeural"

# --- Audio Stitcher Configuration ---
OUTPUT_SAMPLE_RATE = 16000
OUTPUT_CHANNELS = 1

# --- Production FFmpeg Merger Configuration ---
VIDEO_CODEC = "copy"
AUDIO_CODEC = "aac"
FASTSTART = True

# Text-to-Speech (Edge TTS)

TTS_VOICE = "en-US-AriaNeural"

TTS_RATE = "+0%"

TTS_OUTPUT_FILE = OUTPUT_DIR / "translated_audio.mp3"

# Final dubbed video output
DUBBED_VIDEO_OUTPUT = OUTPUT_DIR / "dubbed_video.mp4"


