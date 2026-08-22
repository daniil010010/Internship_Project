from chat_session import ChatSession
import argparse
from chat_session import console
from tools import Tool
from audio_summary_day4 import Whisper
from semantic_search_day3 import Embeddings, VectorStore
from text_to_speech import TextToSpeech


parser = argparse.ArgumentParser(description='System prompt')
parser.add_argument('--prompt', type=str, help="Prompt to enter specific model instructions", dest='prompt', default="Explain as you can")
parser.add_argument('--model', type=str, help="Model to use", default="gpt-4o-mini")
parser.add_argument('--voice', action="store_true", help="Enable voice output")
args = parser.parse_args()
console.print(f"[bold yellow]System prompt:[/bold yellow] {args.prompt}\n[bold yellow]Model:[/bold yellow] {args.model}")



chat = ChatSession(args.model, args.prompt)
whisper = Whisper()
embeddings = Embeddings()
store = VectorStore()
tool = Tool(store, embeddings, chat)
tts = TextToSpeech()



store.load_documents()
store.build_index(embeddings)
while True:
        input_message = input("Please enter your message or enter `quit` to end your Chat Session: ")
        if input_message == "/quit":
            break
        elif input_message == "/update_kb_text":
            doc_name = input("Please enter the doc name you want to add to database: ")
            text = input("Please enter the text you want to add to database: ")
            store.add_document(text, embeddings, doc_name)
            console.print(f"{doc_name} is added to database", style="bold blue")
        elif input_message == "/update_kb_audio":
            audio_file_name = input("Please enter the audio file name you want to add to database: ")
            console.print(
                f"[bold green]Transcribing:[/bold green] "
                f"{audio_file_name}"
            )
            audio_file = whisper.load_file(audio_file_name)
            if not audio_file:
                continue
            transcription = whisper.transcribe(audio_file)
            if not transcription:
                continue
            store.add_document(transcription, embeddings, audio_file_name)
            console.print(f"{audio_file_name} is added to database", style="bold blue")
        elif input_message == "/summarize_session":
            chat.summarize()
        elif input_message == "/change_prompt":
            new_prompt = input("Please enter the new prompt: ")
            chat.prompt = new_prompt
            console.print(f"Prompt is changed to {new_prompt}", style="bold blue")
        elif input_message == "/save_session":
            chat.save_session()
            console.print("Logs saved to logs/.", style="bold green")
        elif input_message == "/load_session":
            json_name = input("Pleas enter the json file name of session you want to load: ")
            chat.load_session(json_name)
            console.print(f"Session loaded from {json_name}", style="bold blue")
        elif input_message == "/search":
            query_message = input("Please enter your message you want to search: ")
            query_with_context = store.search(query_message, embeddings)
            chat.add_input(query_with_context, "user")
            response = chat.send_messages_stream()
            if not response:
                continue
            chat.add_output(response)
            chat.count_tokens(query_with_context, response)
        else:
            console.print(f"[bold green]User:[/bold green] {input_message}")
            chat.add_input(input_message, "user")
            response = chat.send_messages_stream()
            if not response:
                continue
            completed_tool_messages = None
            iterations = 0
            while chat.contains_tool_call(response) and iterations < 10:
                prepared_tool_messages = chat.build_tool_messages(input_message, response)
                completed_tool_messages = chat.run_tools(prepared_tool_messages, input_message, response, tool)
                response = chat.finish_tool_call_stream(completed_tool_messages)
                iterations += 1
                if not response:
                    break
            if not response:
                continue
            chat.add_output(response)
            if completed_tool_messages is not None:
                chat.count_tokens(completed_tool_messages, response, final_count=True)
            else:
                chat.count_tokens(input_message, response)
            chat.clear_tool()
            if args.voice:
                speech_file = tts.create_speech_file()
                tts.create_audio(response.output_text, speech_file)

































