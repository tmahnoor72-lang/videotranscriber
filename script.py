import os
from pathlib import Path
from typing import Optional

from groq import Groq


API_KEY = "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"


class GroqTranscriber:
    """
    Small helper wrapper around the Groq audio transcription endpoint.
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        api_key = api_key or os.environ.get("GROQ_API_KEY") or API_KEY
        self.client = Groq(api_key=api_key)

    def transcribe(
        self,
        audio_path: str | Path,
        *,
        prompt: str | None = None,
        language: str | None = "en",
        temperature: float = 0.0,
    ):
        """
        Send the audio file to Groq Whisper model and return the full payload.
        """
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        with audio_path.open("rb") as audio_file:
            transcription = self.client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-large-v3-turbo",
                prompt=prompt,
                response_format="verbose_json",
                timestamp_granularities=["word", "segment"],
                language=language,
                temperature=temperature,
            )
        return transcription


def transcribe_audio(audio_path: str | Path, **kwargs):
    """
    Convenience function to match the previous script interface.
    """
    transcriber = GroqTranscriber()
    return transcriber.transcribe(audio_path, **kwargs)


if __name__ == "__main__":
    # Example usage
    example_file = os.environ.get("GROQ_DEMO_FILE", "YOUR_AUDIO.wav")
    response = transcribe_audio(example_file)
    print(response)