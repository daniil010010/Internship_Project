from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from rich.console import Console
from constants import TTS_MODEL
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")

console = Console()


class TextToSpeech:
    def __init__(self):
        self.client = OpenAI()


    def create_speech_file(self):
        speech_file_path = Path(__file__).parent / "speech.mp3"
        return speech_file_path


    def create_audio(self, model_input, speech_file_path):
        with self.client.audio.speech.with_streaming_response.create(
            model=TTS_MODEL,
            voice="coral",
            input=model_input,
            instructions="Speak naturally, clearly, and in a friendly tone.",
            response_format="mp3"
        ) as response:
            response.stream_to_file(speech_file_path)
            console.print(f"[bold blue]Speech file saved to [/bold blue]/{speech_file_path}")
