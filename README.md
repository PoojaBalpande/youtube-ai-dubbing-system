# 🎬 AI Video Dubbing System

An AI-powered video dubbing system that downloads a YouTube video, transcribes its speech, translates it to English, generates natural English speech, and produces a fully dubbed MP4 while preserving the original visuals.

---

## 📌 Project Goal

Input:

- YouTube Video URL

Output:

- English Dubbed MP4

The system automatically performs:

1. Download YouTube video
2. Extract audio
3. Transcribe speech
4. Translate to English
5. Generate English speech
6. Replace original audio
7. Export final dubbed video

---

## 🚀 Current Progress

### ✅ Day 1 Completed

- Project setup
- Modular architecture
- Logging system
- YouTube downloader using yt-dlp
- Audio extraction using FFmpeg

### 🔄 Upcoming

- Whisper transcription
- Translation
- Text-to-Speech
- Audio merging
- Multi-speaker support
- Voice cloning

---

## 🏗️ Project Architecture

```
User
 │
 ▼
Enter YouTube URL
 │
 ▼
YouTube Downloader
 │
 ▼
Video (.mp4)
 │
 ▼
Audio Extractor
 │
 ▼
Audio (.wav)
 │
 ▼
Whisper
 │
 ▼
Transcript
 │
 ▼
Translation
 │
 ▼
English Text
 │
 ▼
Edge TTS
 │
 ▼
English Audio
 │
 ▼
FFmpeg
 │
 ▼
Dubbed Video (.mp4)
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.11 |
| Downloader | yt-dlp |
| Speech Recognition | OpenAI Whisper |
| Translation | MarianMT / NLLB |
| Text-to-Speech | Edge-TTS |
| Video Processing | FFmpeg |
| Progress UI | Rich |
| Logging | Python Logging |
| Configuration | python-dotenv |

---

## 📁 Project Structure

```text
youtube-ai-dubbing-system/

├── audio/
├── downloader/
├── transcription/
├── translation/
├── tts/
├── utils/
├── downloads/
├── outputs/
├── temp/
├── logs/
├── docs/
│
├── main.py
├── config.py
├── README.md
├── requirements.txt
└── .env.example
```

---

## ⚙️ Installation

```bash
git clone https://github.com/PoojaBalpande/youtube-ai-dubbing-system.git

cd youtube-ai-dubbing-system

python -m venv .venv

.\.venv\Scripts\activate

pip install -r requirements.txt
```

---

## ▶️ Run

```bash
python main.py
```

---

## 📅 Development Roadmap

- [x] Environment Setup
- [x] Logging
- [x] YouTube Downloader
- [x] Audio Extraction
- [ ] Whisper Transcription
- [ ] Translation
- [ ] Text-to-Speech
- [ ] Audio Replacement
- [ ] Final Dubbed Video

---

## 👩‍💻 Author

**Pooja Balpande**

B.Tech Artificial Intelligence & Data Science

---

## 📄 License

This project is created for learning purposes as part of the Idealabs Digital AI Internship assignment.