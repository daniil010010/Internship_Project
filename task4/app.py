from task1.token_counter import TokenCounter
from task4.audio_summary_day4 import Whisper
from task4.task4_chat_session import ChatSession, console
from task4.task4_prompts import AUDIO_SUMMARIZE_PROMPT

chat = ChatSession(AUDIO_SUMMARIZE_PROMPT)
whisper = Whisper(chat)
token_counter = TokenCounter()

while True:
    input_message = input(
        "Please enter the path to an audio file (supported extensions: '.mp3', '.wav' or '.m4a') or /quit to exit: "
    )
    if input_message == "/quit":
        chat_session = chat.create_logs(token_counter)
        chat.save_logs(chat_session)
        console.print("Logs saved to logs/.", style="bold green")
        break
    console.print(f"[bold green]Transcribing:[/bold green] {input_message}")
    audio_file = whisper.load_file(input_message)
    if not audio_file:
        continue
    transcription = whisper.transcribe(audio_file)
    if not transcription:
        continue
    chat.add_input(transcription, "user")
    response = chat.send_messages()
    if not response:
        continue
    chat.add_output(response.output_text)
    token_counter.count_message(transcription, response.output_text)
