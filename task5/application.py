from rich.console import Console

from task2.task2_token_counter import TokenCounter
from task5.task5_audio_summary import Whisper
from task5.task5_chat_session import ChatSession
from task5.task5_semantic_search import Embeddings, VectorStore
from task5.text_to_speech import TextToSpeech

console = Console()

class Application:
    def __init__(self, chat: ChatSession, whisper: Whisper, tts: TextToSpeech, store: VectorStore, embeddings: Embeddings, voice: bool, token_counter: TokenCounter) -> None:
        self.chat = chat
        self.whisper = whisper
        self.tts = tts
        self.store = store
        self.embeddings = embeddings
        self.voice = voice
        self.token_counter = token_counter

    def run(self) -> None:
        self.store.load_documents()

        doc_embeddings = self.embeddings.create_doc_embeddings(
            self.store.documents
        )

        self.store.embeddings = doc_embeddings
        self.store.build_index(doc_embeddings)
        while True:
            input_message = input("Please enter your message or enter `quit` to end your Chat Session: ")
            if input_message == "/quit":
                return None
            elif input_message == "/help":
                self.show_help()
            elif input_message == "/update_kb_text":
                doc_name = input("Please enter the doc name you want to add to database: ")
                text = input("Please enter the text you want to add to database: ")
                self.store.add_document(text, self.embeddings, doc_name)
                console.print(f"{doc_name} is added to database", style="bold blue")
                self.chat.add_command(
                    "/update_kb_text",
                    document=doc_name
                )
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
                self.chat.add_command(
                    "/update_kb_audio",
                    file=audio_file_name
                )
                console.print(f"{audio_file_name} is added to database", style="bold blue")
            elif input_message == "/summarize_session":
                self.chat.summarize()
                self.chat.add_command(
                    "/summarize_session"
                )
            elif input_message == "/change_prompt":
                new_prompt = input("Please enter the new prompt: ")
                self.chat.prompt = new_prompt
                console.print(f"Prompt is changed to {new_prompt}", style="bold blue")
                self.chat.add_command(
                    "/change_prompt",
                    prompt=new_prompt
                )
            elif input_message == "/save_session":
                self.chat.save_session()
            elif input_message == "/load_session":
                json_name = input("Pleas enter the json file name of session you want to load: ")
                self.chat.load_session(json_name)
                console.print(f"Session loaded from {json_name}", style="bold blue")
                self.chat.add_command(
                    "/load_session",
                    file=json_name
                )
            elif input_message == "/search":
                query_message = input("Please enter your message you want to search: ")
                console.print("[bold yellow]System:[/bold yellow] Creating query embedding")
                query_embedding = self.embeddings.create_embedding(query_message)
                result = self.store.search(query_embedding)
                context = self.store.create_context(result)
                query_with_context = self.store.create_query_with_context(query_message, context)
                self.chat.add_input(query_with_context, "user")
                response = self.chat.send_search_messages()
                if not response:
                    continue
                self.chat.add_output(response)
                self.token_counter.count_tokens(query_with_context, response)
                self.chat.add_command(
                    "/search",
                    query=query_message
                )
            else:
                console.print(f"[bold green]User:[/bold green] {input_message}")
                self.chat.add_input(input_message, "user")
                response = self.chat.send_messages_stream()
                if not response:
                    continue
                response = self.chat.process_tool_calls(input_message, response)
                if not response:
                    continue
                self.chat.add_output(response)
                if self.voice:
                    speech_file = self.tts.create_speech_file()
                    self.tts.create_audio(response.output_text, speech_file)

    def show_help(self) -> None:
        console.print("[bold blue]Available commands:[/bold blue]")
        console.print("/search - Search the knowledge base")
        console.print("/update_kb_text - Add a text document to the knowledge base")
        console.print("/update_kb_audio - Add an audio file to the knowledge base")
        console.print("/summarize_session - Summarize the current session")
        console.print("/change_prompt - Change the system prompt")
        console.print("/save_session - Save the current session")
        console.print("/load_session - Load a saved session")
        console.print("/help - Show available commands")
        console.print("/quit - Exit the application")



