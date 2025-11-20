import os
import shutil
import subprocess
import uuid
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename
from yt_dlp import YoutubeDL

from script import transcribe_audio

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "downloads"
OUTPUT_DIR.mkdir(exist_ok=True)


def download_video(url: str) -> Path:
    """
    Download the YouTube video using yt-dlp and return the file path.
    """
    download_id = uuid.uuid4().hex
    outtmpl = str(OUTPUT_DIR / f"{download_id}.%(ext)s")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": outtmpl,
        "quiet": True,
        "no_warnings": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        downloaded_file = Path(ydl.prepare_filename(info))

    return downloaded_file


def convert_to_wav(input_path: Path) -> Path:
    """
    Use ffmpeg to convert the downloaded media file into WAV audio.
    """
    wav_name = secure_filename(f"{input_path.stem}.wav")
    wav_path = input_path.with_name(wav_name)

    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_path),
        "-ac",
        "1",
        "-ar",
        "16000",
        str(wav_path),
    ]
    process = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )

    if process.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {process.stderr}")

    return wav_path


def cleanup_files(*paths: Path) -> None:
    for path in paths:
        if path and path.exists():
            if path.is_file():
                path.unlink(missing_ok=True)
            elif path.is_dir():
                shutil.rmtree(path, ignore_errors=True)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", transcription=None, error=None)


@app.route("/transcribe", methods=["POST"])
def transcribe_route():
    video_url = request.form.get("video_url", "").strip()
    prompt = request.form.get("prompt", "").strip() or None

    if not video_url:
        flash("Please provide a valid YouTube URL.", "danger")
        return redirect(url_for("index"))

    downloaded_path: Path | None = None
    wav_path: Path | None = None

    try:
        downloaded_path = download_video(video_url)
        wav_path = convert_to_wav(downloaded_path)
        transcription = transcribe_audio(wav_path, prompt=prompt)
        text = getattr(transcription, "text", None) or transcription.get("text")

        segments = None
        if hasattr(transcription, "segments"):
            segments = transcription.segments
        elif isinstance(transcription, dict):
            segments = transcription.get("segments")

        return render_template(
            "index.html",
            transcription=text,
            segments=segments,
            video_url=video_url,
            error=None,
        )
    except Exception as exc:
        app.logger.exception("Transcription failed")
        flash(str(exc), "danger")
        return redirect(url_for("index"))
    finally:
        cleanup_files(downloaded_path, wav_path)


if __name__ == "__main__":
    app.run(debug=True)

