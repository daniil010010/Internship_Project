from chat_session import ChatSession
import argparse
from chat_session import console
from tools import Tool

parser = argparse.ArgumentParser(description='System prompt')
parser.add_argument('--prompt', type=str, help="Prompt to enter specific model instructions", dest='prompt', default="Explain as you can")
args = parser.parse_args()
console.print(f"[bold yellow]System prompt:[/bold yellow] {args.prompt}")

chat = ChatSession(args.prompt)

tool = Tool()

start_message = input("Please enter the `/start` to start your Chat Session or enter `/quit` to end your Chat Session: ")
while True:
    if start_message == "/start":
        input_message = input("Please enter your message or enter `/quit` to end your Chat Session: ")
        if input_message == "/quit":
            summary = chat.summarize()
            if not summary:
                break
            chat.count_tokens("", summary)
            chat.save_logs(summary)
            console.print("Logs saved to logs/.", style="bold green")
            break
        console.print(f"[bold green]User:[/bold green] {input_message}")
        chat.add_input(input_message,"user")
        response = chat.send_messages()
        if not response:
            break
        chat.add_output(response)
        chat.count_tokens(input_message, response)
        iterations = 0
        while chat.contains_tool_call(response) and iterations < 10:
            prepared_tool_messages = chat.build_tool_messages(input_message, response)
            completed_tool_messages = chat.run_tools(prepared_tool_messages, input_message, response, tool)
            response = chat.finish_tool_call(completed_tool_messages)
            iterations += 1
            if not response:
                break
        chat.add_output(response)
        chat.count_tokens(completed_tool_messages, response, final_count=True)
        chat.clear_tool()
    elif start_message == "/quit":
        break
    else:
        console.print("Invalid command", style="bold red")
        start_message = input("Please enter the `/start` to start your Chat Session or enter `/quit` to end your Chat Session: ")
        continue



