from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
from openai import APIConnectionError, AuthenticationError, RateLimitError, BadRequestError, OpenAIError
from rich.console import Console
import os


load_dotenv()
API_KEY = os.getenv("API_KEY")

console = Console()

AUDIO_MODEL = "whisper-1"

class Whisper:
    def __init__(self):
        self.client = OpenAI(api_key=API_KEY)

    def load_file(self, path):
        path = Path(path)
        if not path.exists():
            console.print(f"[bold red]Error.[/bold red] {path} does not exist.")
            return None
        if path.suffix.lower() in {".mp3", ".wav", ".m4a"}:
            audio_file = open(path, 'rb')
            return audio_file
        else:
            console.print("[bold red]Unsupported file format.[/bold red] Supported formats: .mp3, .wav, .m4a.")
            return None

    def transcribe(self, file):
        try:
            transcription = self.client.audio.transcriptions.create(
                model=AUDIO_MODEL,
                file=file
            )
        except APIConnectionError:
            console.print("[bold red]Connection Error.[/bold red] Please check your Internet connection and try again.")
            return None
        except AuthenticationError:
            console.print("[bold red]Authentication failed.[/bold red] Please check your API key.")
            return None
        except RateLimitError:
            console.print("[bold red]Rate limit exceeded or API quota reached.[/bold red] Please try again later.")
            return None
        except BadRequestError:
            console.print("[bold red]Invalid request.[/bold red] Please make sure the audio file is valid and supported.")
            return None
        except OpenAIError:
            console.print("[bold red]An unexpected OpenAI error occurred.[/bold red] Please try again later.")
            return None
        except Exception as e:
            console.print(f"[bold red]Unexpected Error.[/bold red] {e}")
            return None
        finally:
            file.close()
        transcription = transcription.text
        console.print(f"[bold yellow]Transcription:[/bold yellow] {transcription}")
        return transcription



