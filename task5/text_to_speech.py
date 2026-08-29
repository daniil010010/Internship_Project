from openai import OpenAI
from rich.console import Console

from task1.config import API_KEY
from task5.task5_constants import TTS_MODEL
from pathlib import Path


console = Console()


class TextToSpeech:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=API_KEY)


    def create_speech_file(self) -> Path:
        speech_dir = Path(__file__).resolve().parent / "speech"
        speech_dir.mkdir(exist_ok=True)

        return speech_dir / "speech.mp3"


    def create_audio(self, model_input: str, speech_file_path: Path) -> None:
        with self.client.audio.speech.with_streaming_response.create(
            model=TTS_MODEL,
            voice="coral",
            input=model_input,
            instructions="Speak naturally, clearly, and in a friendly tone.",
            response_format="mp3"
        ) as response:
            response.stream_to_file(speech_file_path)
            console.print(f"[bold blue]Speech file saved to [/bold blue]/{speech_file_path}")
