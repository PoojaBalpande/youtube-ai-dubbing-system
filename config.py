from pathlib import Path
import os
from dotenv import load_dotenv

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent

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


