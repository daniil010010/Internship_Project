from pathlib import Path
from typing import BinaryIO

from rich.console import Console

from task4.task4_chat_session import ChatSession
from task4.task4_constants import AUDIO_MODEL

console = Console()


class Whisper:
    def __init__(self, chat: ChatSession) -> None:
        self.chat = chat
        self.client = chat.client

    def load_file(self, path: str) -> BinaryIO | None:
        path = Path(path)
        if not path.exists():
            console.print(f"[bold red]Error.[/bold red] {path} does not exist.")
            return None
        if path.suffix.lower() in {".mp3", ".wav", ".m4a"}:
            audio_file = open(path, "rb")
            return audio_file
        else:
            console.print(
                "[bold red]Unsupported file format.[/bold red] Supported formats: .mp3, .wav, .m4a."
            )
            return None

    def transcribe(self, file: BinaryIO) -> str | None:
        try:
            transcription = self.client.audio.transcriptions.create(
                model=AUDIO_MODEL, file=file
            )
        except Exception as error:
            self.chat.handle_error(error)
            return None
        finally:
            file.close()
        transcription = transcription.text
        console.print(f"[bold yellow]Transcription:[/bold yellow] {transcription}")
        return transcription
