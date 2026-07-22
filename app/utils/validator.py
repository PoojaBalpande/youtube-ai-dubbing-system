"""
Configuration validation module.

Validates application configurations, credentials, models, and external
system dependency availability (like FFmpeg/FFprobe) before executing pipeline.
Automatically creates any missing application directories.
"""

import os
import shutil
from pathlib import Path
from config import settings as config
from app.utils.logger import get_logger

logger = get_logger(__name__)

def validate_config() -> None:
    """
    Perform startup validation of directories, credentials, configs, and dependencies.
    """
    logger.info("Initializing system configuration and dependency validation...")

    # 1. Directory creation/validation
    directories = [
        Path(getattr(config, "DOWNLOAD_DIR", "downloads")),
        Path(getattr(config, "OUTPUT_DIR", "outputs")),
        Path(getattr(config, "TEMP_DIR", "temp")),
        Path(getattr(config, "TEMP_DIR", "temp")) / "tts",
        Path(getattr(config, "TEMP_DIR", "temp")) / "tts_wav",
        Path(getattr(config, "LOG_DIR", "logs")),
    ]
    for directory in directories:
        try:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Directory verified: {directory}")
        except Exception as error:
            raise RuntimeError(f"Failed to verify or create directory '{directory}': {error}")

    # 2. Translate Provider Credentials and configuration
    provider = getattr(config, "TRANSLATOR_PROVIDER", "groq")
    if provider == "groq":
        api_key = getattr(config, "GROQ_API_KEY", "") or os.environ.get("GROQ_API_KEY", "")
        if not api_key:
            raise ValueError(
                "TRANSLATOR_PROVIDER is set to 'groq', but GROQ_API_KEY is not configured in .env or config.py."
            )
        model = getattr(config, "GROQ_MODEL", "") or os.environ.get("GROQ_MODEL", "")
        if not model:
            raise ValueError(
                "TRANSLATOR_PROVIDER is set to 'groq', but GROQ_MODEL is not configured in .env or config.py."
            )
    elif provider == "marian":
        pass
    else:
        logger.warning(f"Unknown TRANSLATOR_PROVIDER '{provider}'. Validation skipped.")

    # 3. Whisper model config
    whisper_model = getattr(config, "WHISPER_MODEL", "")
    if not whisper_model:
        raise ValueError("WHISPER_MODEL is not configured in config.py.")

    # 4. TTS Voice name configuration
    voice = getattr(config, "VOICE", "") or os.environ.get("VOICE", "")
    if not voice:
        raise ValueError("VOICE name is not configured in config.py or .env.")

    # 5. FFmpeg / FFprobe availability
    if not shutil.which("ffmpeg"):
        raise RuntimeError("FFmpeg executable not found on system PATH. FFmpeg is required for video extraction and merging.")
    if not shutil.which("ffprobe"):
        raise RuntimeError("FFprobe executable not found on system PATH. FFprobe is required for audio duration calculation.")

    logger.info("Configuration and dependency validation completed successfully.")
