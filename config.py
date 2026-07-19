from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent

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