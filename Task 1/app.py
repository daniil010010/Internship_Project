import argparse

from chat_session import ChatSession, console
from prompts import DEFAULT_PROMPT

parser = argparse.ArgumentParser(description="System prompt")
parser.add_argument(
    "--prompt",
    type=str,
    help="Prompt to enter specific model instructions",
    dest="prompt",
    default=DEFAULT_PROMPT,
)
args = parser.parse_args()
console.print(f"[bold yellow]System prompt:[/bold yellow] {args.prompt}")

chat = ChatSession(args.prompt)

while True:
    input_message = input(
        "Please enter your message or enter `/quit` to end your Chat Session: "
    )

    if input_message == "/quit":
        chat_session = chat.create_logs()
        chat.save_logs(chat_session)
        console.print("Logs saved to logs/.", style="bold green")
        break

    console.print(f"[bold green]User:[/bold green] {input_message}")
    chat.add_input(input_message, "user")
    response = chat.send_messages("user", input_message)
    chat.add_output(response)
    chat.count_tokens(input_message, response)
