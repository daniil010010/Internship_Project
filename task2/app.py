import argparse

from task2.task2_chat_session import ChatSession, console
from task2.task2_prompts import DEFAULT_PROMPT
from task2.task2_token_counter import TokenCounter
from task2.tools import Tool

parser = argparse.ArgumentParser(description='System prompt')
parser.add_argument('--prompt', type=str, help="Prompt to enter specific model instructions", dest='prompt', default=DEFAULT_PROMPT)
args = parser.parse_args()
console.print(f"[bold yellow]System prompt:[/bold yellow] {args.prompt}")


chat = ChatSession(args.prompt)

token_counter = TokenCounter()
tool = Tool(chat)

chat.tool = tool
chat.token_counter = token_counter


while True:
    input_message = input("Please enter your message or enter `/quit` to end your Chat Session: ")

    if input_message == "/quit":
        summary = chat.summarize()
        if not summary:
            break
        chat_session = chat.create_logs(summary)
        chat.save_logs(chat_session)
        console.print("Logs saved to logs/.", style="bold green")
        break

    token_counter.reset_tool_tokens()

    console.print(f"[bold green]User:[/bold green] {input_message}")
    chat.add_input(input_message, "user")
    response = chat.send_messages()

    if not response:
        continue

    if chat.contains_tool_call(response):
        response = chat.process_tool_calls(
            input_message,
            response
        )
    else:
        token_counter.count_tokens(
            input_message,
            response,
            show=True
        )

    if not response:
        continue

    if response.output_text:
        chat.add_output(response)







