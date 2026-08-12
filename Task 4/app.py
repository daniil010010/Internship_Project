from chat_session import ChatSession
from chat_session import console
from audio_summary_day4 import Whisper


chat = ChatSession("Summarize the provided audio transcription concisely. Extract the main ideas, important facts, conclusions, and key points. "
                   "Do not add information that is not present in the transcription. Use clear and structured language.")
whisper = Whisper()

while True:
    input_message = input("Please enter the path to an audio file (supported extensions: '.mp3', '.wav' or '.m4a') or /quit to exit: ")
    if input_message == "/quit":
        chat.save_logs("")
        console.print("Logs saved to logs/.", style="bold green")
        break
    console.print(f"[bold green]Transcribing:[/bold green] {input_message}")
    audio_file = whisper.load_file(input_message)
    if not audio_file:
        continue
    transcription = whisper.transcribe(audio_file)
    if not transcription:
        continue
    chat.add_input(transcription,"user")
    response = chat.send_messages()
    if not response:
        continue
    chat.add_output(response)
    chat.count_tokens(transcription, response)




