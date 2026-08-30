import argparse

from task2.task2_token_counter import TokenCounter
from task5.application import Application
from task5.task5_audio_summary import Whisper
from task5.task5_chat_session import ChatSession, console
from task5.task5_constants import MODEL
from task5.task5_prompts import DEFAULT_PROMPT
from task5.task5_semantic_search import Embeddings, VectorStore
from task5.text_to_speech import TextToSpeech
from task5.task5_tools import Tool


parser = argparse.ArgumentParser(description='System prompt')
parser.add_argument('--prompt', type=str, help="Prompt to enter specific model instructions", dest='prompt', default=DEFAULT_PROMPT)
parser.add_argument('--model', type=str, help="Model to use", default=MODEL)
parser.add_argument('--voice', action="store_true", help="Enable voice output")
args = parser.parse_args()
console.print(f"[bold yellow]System prompt:[/bold yellow] {args.prompt}\n[bold yellow]Model:[/bold yellow] {args.model}\n")



chat = ChatSession(args.prompt, args.model)
whisper = Whisper(chat)
embeddings = Embeddings()
store = VectorStore()
tool = Tool(store, embeddings, chat)
tts = TextToSpeech()
token_counter = TokenCounter()

chat.token_counter = token_counter
chat.tool = tool

application = Application(chat, whisper, tts, store, embeddings, args.voice, token_counter)

application.run()

































