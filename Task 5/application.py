from text_to_speech import TextToSpeech
from task5_chat_session import ChatSession
from task5_semantic_search import Embeddings
from task5_semantic_search import VectorStore
from task5_audio_summary import Whisper
from rich.console import Console
import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent / "Task 2")
)

from task2_token_counter import TokenCounter

console = Console()

class Application:
    def __init__(self, chat: ChatSession, whisper: Whisper, tts: TextToSpeech, store: VectorStore, embeddings: Embeddings, voice: bool, token_counter: TokenCounter):
        self.chat = chat
        self.whisper = whisper
        self.tts = tts,
        self.store = store
        self.embeddings = embeddings
        self.voice = voice
        self.token_counter = token_counter

    def run(self):
        self.store.load_documents()
        self.embeddings.create_doc_embeddings(self.store.documents)
        while True:
            input_message = input("Please enter your message or enter `quit` to end your Chat Session: ")
            if input_message == "/quit":
                return None
            elif input_message == "/update_kb_text":
                doc_name = input("Please enter the doc name you want to add to database: ")
                text = input("Please enter the text you want to add to database: ")
                self.store.add_document(text, self.embeddings, doc_name)
                console.print(f"{doc_name} is added to database", style="bold blue")
            elif input_message == "/update_kb_audio":
                audio_file_name = input("Please enter the audio file name you want to add to database: ")
                console.print(
                    f"[bold green]Transcribing:[/bold green] "
                    f"{audio_file_name}"
                )
                audio_file = self.whisper.load_file(audio_file_name)
                if not audio_file:
                    continue
                transcription = self.whisper.transcribe(audio_file)
                if not transcription:
                    continue
                self.store.add_document(transcription, self.embeddings, audio_file_name)
                console.print(f"{audio_file_name} is added to database", style="bold blue")
            elif input_message == "/summarize_session":
                self.chat.summarize()
            elif input_message == "/change_prompt":
                new_prompt = input("Please enter the new prompt: ")
                self.chat.prompt = new_prompt
                console.print(f"Prompt is changed to {new_prompt}", style="bold blue")
            elif input_message == "/save_session":
                self.chat.save_session()
                console.print("Logs saved to logs/.", style="bold green")
            elif input_message == "/load_session":
                json_name = input("Pleas enter the json file name of session you want to load: ")
                self.chat.load_session(json_name)
                console.print(f"Session loaded from {json_name}", style="bold blue")
            elif input_message == "/search":
                query_message = input("Please enter your message you want to search: ")
                result = self.store.search(query_message)
                query_with_context = self.store.create_context(result)
                self.chat.add_input(query_with_context, "user")
                response = self.chat.send_messages_stream()
                if not response:
                    continue
                self.chat.add_output(response)
                self.token_counter.count_tokens(query_with_context, response)
            else:
                console.print(f"[bold green]User:[/bold green] {input_message}")
                self.chat.add_input(input_message, "user")
                response = self.chat.send_messages_stream()
                if not response:
                    continue
                self.chat.process_tool_call(response)
                if not response:
                    continue
                self.chat.add_output(response)
                if self.voice:
                    speech_file = self.tts.create_speech_file()
                    self.tts.create_audio(response.output_text, speech_file)


