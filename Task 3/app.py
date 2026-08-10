from chat_session import ChatSession
import argparse
from chat_session import console
from semantic_search_day3 import Embeddings

parser = argparse.ArgumentParser(description='System prompt')
parser.add_argument('--prompt', type=str, help="Prompt to enter specific model instructions", dest='prompt', default="Explain as you can")
args = parser.parse_args()
console.print(f"[bold yellow]System prompt:[/bold yellow] {args.prompt}")

chat = ChatSession(args.prompt)
embeddings = Embeddings()

start_message = input("Please enter the `/start` to start your Chat Session or enter `/quit` to end your Chat Session: ")
embeddings.load_documents()
embeddings.create_doc_embeddings()
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
        query_embedding = embeddings.create_input_embeddings(input_message)
        embeddings.compare_embeddings(query_embedding)
        embeddings.sort_scores()
        context = embeddings.create_context()
        query = embeddings.create_query_with_context(input_message, context)
        chat.add_input(query,"user")
        response = chat.send_messages()
        if not response:
            break
        chat.add_output(response)
        chat.count_tokens(query, response)
    elif start_message == "/quit":
        break
    else:
        console.print("Invalid command", style="bold red")
        start_message = input("Please enter the `/start` to start your Chat Session or enter `/quit` to end your Chat Session: ")
        continue



