# YouTube AI Video Dubbing System

An end-to-end, production-grade AI-powered YouTube Video Dubbing pipeline built with Python. 
This application transcribes, translates, aligns, synthesizes, and merges multilingual voiceovers onto original YouTube videos with high temporal precision.

---

## 1. Project Overview & Architecture

The YouTube AI Video Dubbing System converts a YouTube video into a dubbed version by orchestrating multiple deep learning and signal processing modules in a pipeline.

### Pipeline Diagram

```
[YouTube Video URL]
       │
       ▼
 ┌───────────┐
 │ Download  │  (yt-dlp)
 └─────┬─────┘
       ▼
 ┌───────────┐
 │ Extract   │  (FFmpeg audio extraction)
 └─────┬─────┘
       ▼
 ┌───────────┐
 │ Transcribe│  (OpenAI Whisper -> TranscriptSegment[])
 └─────┬─────┘
       ▼
 ┌───────────┐
 │ Translate │  (ContextBuilder -> GroqTranslator / MarianMT Fallback)
 └─────┬─────┘
       ▼
 ┌───────────┐
 │    TTS    │  (Segment-wise speech generation with Edge-TTS)
 └─────┬─────┘
       ▼
 ┌───────────┐
 │  Timing   │  (Expected vs. Actual duration analysis & rate-adjustment sync)
 └─────┬─────┘
       ▼
 ┌───────────┐
 │  Stitch   │  (PCM WAV compilation & timeline silence padding)
 └─────┬─────┘
       ▼
 ┌───────────┐
 │   Merge   │  (Production FFmpeg layout: c:v copy & c:a aac)
 └─────┬─────┘
       ▼
 [Final Dubbed Video (.mp4)]
```

### Architecture Diagram

```
                           ┌──────────────────────────┐
                           │         main.py          │ (Orchestrator)
                           └─────────────┬────────────┘
                                         │
      ┌───────────────┬──────────────────┼───────────────┬────────────────┐
      ▼               ▼                  ▼               ▼                ▼
┌───────────┐   ┌───────────┐      ┌───────────┐   ┌───────────┐    ┌───────────┐
│Downloader │   │ Extractor │      │  Whisper  │   │Translator │    │SegmentTTS │
│ (yt-dlp)  │   │ (FFmpeg)  │      │  Engine   │   │  Factory  │    │(Edge-TTS) │
└───────────┘   └───────────┘      └───────────┘   └─────┬─────┘    └───────────┘
                                                         │
                                               ┌─────────┴─────────┐
                                               ▼                   ▼
                                         ┌───────────┐       ┌───────────┐
                                         │   Groq    │       │  Marian   │
                                         │Translator │       │Translator │
                                         └───────────┘       └───────────┘
```

---

## 2. Folder Structure

```text
youtube-ai-dubbing-system/
│
├── audio/                      # Audio utilities
│   ├── converter.py            # MP3 to standardized WAV format converter
│   ├── extractor.py            # Extracts audio tracks from video files
│   └── merger.py               # Merges dubbed audio tracks onto videos
│
├── downloader/                 # Video downloading module
│   └── youtube.py              # Download YouTube streams using yt-dlp
│
├── models/                     # Shared data schemas
│   └── segment.py              # TranscriptSegment & SegmentAudio definitions
│
├── timing/                     # Synchronization & timeline compiling
│   ├── audio_stitcher.py       # Stitches segment audios with silence padding
│   ├── duration.py             # Computes expected vs actual durations via ffprobe
│   └── sync.py                 # Synchronization strategy thresholds
│
├── transcription/              # Speech-to-Text module
│   └── whisper_engine.py       # Transcribes speech into segments via Whisper
│
├── translation/                # Translation module
│   ├── base.py                 # Abstract base strategy
│   ├── context_builder.py      # Preserves text context using window grouping
│   ├── groq.py                 # Primary translator using Groq SDK
│   ├── marian_translator.py    # Fallback offline translator using MarianMT
│   ├── text_splitter.py        # Splits transcripts into manageable chunks
│   └── translator.py           # Swappable strategy wrapper & factory registry
│
├── tts/                        # Text-to-Speech module
│   ├── tts_engine.py           # Segment-wise speech synthesis engine
│   └── voice_selector.py       # Selects appropriate voices dynamically
│
├── utils/                      # Core helpers
│   ├── logger.py               # Standardized logging setup
│   └── validator.py            # Startup configuration & dependency checks
│
├── .env.example                # Template for environment configuration
├── config.py                   # Centralized application configurations
├── main.py                     # Pipeline execution runner
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

---

## 3. Installation & Setup

### Prerequisites
* **Python 3.10+**
* **FFmpeg & FFprobe**: Must be installed and added to your system environment `PATH`.

### Required Dependencies

The system utilizes the following core packages:
* `groq` - Official Groq SDK client
* `openai-whisper` - Speech recognition engine
* `edge-tts` - High-quality asynchronous speech synthesis
* `transformers` & `sacremoses` & `sentencepiece` - Local neural machine translation model
* `yt-dlp` - Stable video downloading
* `python-dotenv` - Environment configurations

To install all dependencies:
```bash
pip install -r requirements.txt
```

### Environment Setup

Create a `.env` file in the root directory:
```env
# Credentials
GROQ_API_KEY=gsk_your_actual_groq_api_key_here

# Provider Configuration
TRANSLATION_PROVIDER=groq
GROQ_MODEL=mixtral-8x7b-32768

# Text-to-Speech Voice
VOICE=en-US-GuyNeural

# Log Level Configuration (INFO / DEBUG / WARNING / ERROR)
LOG_LEVEL=INFO
```

---

## 4. How the Translation System Works

### Context-Preserving Translation
Rather than translating segments independently, the system uses a **Context Builder**:
1. Merges consecutive segments into sliding windows of size `CONTEXT_WINDOW` (default: 3).
2. Sends the merged paragraphs to the translator, preventing the loss of grammatical and context relationships.
3. Splits the translated sentences back into words and redistributes them proportionally to each original segment based on original word count shares.

### Groq Translator & MarianMT Fallback
* **Primary Translator**: The system uses `GroqTranslator` by default to query high-speed, high-quality models (such as `mixtral-8x7b-32768` or `llama3-8b-8192`) on Groq.
* **Error Fallback**: If the Groq API key is missing, invalid, or hits a rate limit, the system logs a warning, falls back to `MarianTranslator` dynamically, and continues the translation using the offline Helsinki-NLP transformer model without breaking the pipeline run.

---

## 5. Timing Synchronization & Stitching

### expected vs. actual Analysis
For each segment:
* **Expected duration** is computed from the Whisper timestamps (`end - start`).
* **Actual duration** is measured from the generated Segment Edge-TTS MP3 clip using `ffprobe`.
* **Sync decision**:
  * **Shorter clips**: Pad silence at the end of the segment to match the expected timeline space.
  * **Longer clips**: Apply speaking-rate adjustment (capped at `MAX_TTS_RATE_CHANGE`, default 15%) and regenerate the clip.

### Audio Stitcher
The `AudioStitcher` reads the segment timeline metadata and combines the segment-level normalized WAV clips:
* Automatically inserts silence gap frames to align segment boundaries with target timestamps.
* Prevents overlapping audio by positioning overlapping sections sequentially.
* Fills missing segments with silence equal to their expected duration.

---

## 6. Running the Project

Run the pipeline by executing the main script:
```bash
python main.py
```
Enter a YouTube URL when prompted (e.g., `https://www.youtube.com/watch?v=jNQXAC9IVRw`). The final video will be output to `outputs/dubbed_video.mp4`.

---

## 7. Troubleshooting

* **FFmpeg executable not found**: Make sure FFmpeg is installed and added to your system `PATH`. Check with `ffmpeg -version` in your terminal.
* **Groq API Connection / Rate Limit**: The system will automatically fall back to local MarianMT if Groq fails or is unconfigured. Make sure your internet connection is stable.