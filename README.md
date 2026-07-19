# 🎬 AI Video Dubbing System

An end-to-end AI-powered YouTube Video Dubbing pipeline built with Python.

This project automatically:

- Downloads a YouTube video
- Extracts high-quality audio
- Converts speech into text using OpenAI Whisper
- (Upcoming) Translates the transcript
- (Upcoming) Generates AI voice using Edge TTS
- (Upcoming) Merges dubbed audio with the original video

---

# 🚀 Features

## ✅ Completed

- YouTube video downloader using yt-dlp
- Audio extraction using FFmpeg
- Speech-to-text transcription using OpenAI Whisper
- Structured logging
- Configuration-driven architecture
- Modular project structure
- Production-style class design

## 🚧 Upcoming

- Text Translation
- AI Voice Generation (Edge TTS)
- Audio Replacement
- Final Video Rendering
- Multi-language Support

---

# 📂 Project Structure

```text
youtube-ai-dubbing-system/

├── downloader/
│   └── youtube.py
│
├── audio/
│   ├── extractor.py
│   └── merger.py
│
├── transcription/
│   └── whisper_engine.py
│
├── translation/
│   └── translator.py
│
├── tts/
│   └── edge_tts_engine.py
│
├── utils/
│   ├── logger.py
│   └── helpers.py
│
├── downloads/
├── temp/
├── outputs/
│
├── config.py
├── main.py
├── requirements.txt
└── README.md
```

---

# ⚙️ Tech Stack

- Python 3.11
- OpenAI Whisper
- PyTorch
- yt-dlp
- FFmpeg
- pathlib
- logging

---

# 📌 Current Pipeline

```text
YouTube URL
      │
      ▼
Download Video
      │
      ▼
Extract Audio
      │
      ▼
Whisper Speech Recognition
      │
      ▼
Transcript (.txt)
```

---

# 🧠 Architecture

```text
main.py

     │

     ▼

YouTubeDownloader

     │

     ▼

AudioExtractor

     │

     ▼

WhisperEngine

     │

     ▼

Transcript
```

---

# 🧩 Modules

## YouTubeDownloader

Responsible for downloading YouTube videos.

## AudioExtractor

Responsible for extracting WAV audio using FFmpeg.

## WhisperEngine

Responsible for:

- Loading Whisper model
- Speech Recognition
- Saving transcript

---

# 📝 Logging

Every module uses a dedicated logger.

Example:

```
Loading Whisper model...
Downloading video...
Extracting audio...
Starting transcription...
Transcription completed successfully.
Transcript saved...
```

---

# 🔧 Configuration

Configuration is managed through `config.py`.

Examples:

- Whisper Model
- Device
- Output Directories
- Beam Size
- Temperature

---

# 📅 Development Progress

## ✅ Day 1

- Project setup
- Logging
- Downloader
- Audio Extraction

## ✅ Day 2

- Whisper Integration
- Speech Recognition
- Transcript Generation

## 🔜 Day 3

- Translation