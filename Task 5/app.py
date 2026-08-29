from application import Application
from task5_chat_session import ChatSession
import argparse
from task5_chat_session import console
from task5_semantic_search import Embeddings, VectorStore
from text_to_speech import TextToSpeech
from task5_constants import MODEL
from pathlib import Path
import sys
from task5_prompts import DEFAULT_PROMPT
from task5_audio_summary import Whisper


sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent / "Task 2")
)

from task2_token_counter import TokenCounter


parser = argparse.ArgumentParser(description='System prompt')
parser.add_argument('--prompt', type=str, help="Prompt to enter specific model instructions", dest='prompt', default=DEFAULT_PROMPT)
parser.add_argument('--model', type=str, help="Model to use", default=MODEL)
parser.add_argument('--voice', action="store_true", help="Enable voice output")
args = parser.parse_args()
console.print(f"[bold yellow]System prompt:[/bold yellow] {args.prompt}\n[bold yellow]Model:[/bold yellow] {args.model}")



chat = ChatSession(args.model, args.prompt)
whisper = Whisper()
embeddings = Embeddings()
store = VectorStore()
tts = TextToSpeech()
token_counter = TokenCounter()

application = Application(chat, whisper, tts, store, embeddings, args.voice, token_counter)

application.run()

































