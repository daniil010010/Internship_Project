from chat_session import ChatSession
import argparse
from chat_session import console

parser = argparse.ArgumentParser(description='System prompt')
parser.add_argument('--prompt', type=str, help="Prompt to enter specific model instructions", dest='prompt', default="Explain as you can")
args = parser.parse_args()
console.print(f"[bold yellow]System prompt:[/bold yellow] {args.prompt}")

chat = ChatSession(args.prompt)

start_message = input("Please enter the `/start` to start your Chat Session or enter `/quit` to end your Chat Session: ")
while True:
    if start_message == "/start":
        input_message = input("Please enter your message or enter `/quit` to end your Chat Session: ")
        if input_message == "/quit":
            chat.save_logs()
            console.print("Logs saved to logs/.", style="bold green")
            break
        console.print(f"[bold green]User:[/bold green] {input_message}")
        chat.send_messages("user", input_message)
    elif start_message == "/quit":
        break
    else:
        console.print("Invalid command", style="bold red")
        start_message = input("Please enter the `/start` to start your Chat Session or enter `/quit` to end your Chat Session: ")
        continue



