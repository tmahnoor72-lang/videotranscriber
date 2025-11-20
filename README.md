# Groq Video Transcriber

A full-stack YouTube transcriber that downloads a video with `yt-dlp`, converts the audio with `ffmpeg`, and submits it to Groq's Whisper (`whisper-large-v3-turbo`) model. The result is rendered in a modern Bootstrap UI that also lists timestamped segments when available.

## Features
- Paste any public YouTube URL and transcribe it in one click.
- Audio conversion handled locally via `ffmpeg` (mono, 16 kHz WAV for best Whisper performance).
- Backend built with Flask; frontend uses Bootstrap 5 with custom glassmorphic styling.
- Displays overall transcript plus optional word/segment timestamps from Groq.

## Requirements
- Python 3.11+
- `ffmpeg` available on `PATH` (preinstalled per user request, otherwise download from https://ffmpeg.org/).
- Groq API access.

## Installation
```bash
python -m venv .venv
.venv\Scripts\activate             # Windows
pip install -r requirements.txt
```

## Configuration
The project currently defaults to a baked-in Groq API key (per instructions). For production, set environment variables instead:

```powershell
setx GROQ_API_KEY "<your_key>"
setx FLASK_SECRET_KEY "<random_secret>"
```

## Running the App
```bash
flask --app app run --debug
```
Then open http://127.0.0.1:5000 and submit a YouTube URL.

## Workflow
1. User submits a URL from the UI.
2. `yt-dlp` downloads the best available audio.
3. `ffmpeg` normalizes to mono/16k WAV.
4. Audio is passed to `script.py` (`GroqTranscriber`) for transcription.
5. The UI displays the transcript and segment list.

## Notes
- Temporary downloads are stored beneath `downloads/` and removed after each request.
- For long videos, consider streaming progress or adding async tasks.
- Keep your Groq API key secret; rotate it frequently in real deployments.

