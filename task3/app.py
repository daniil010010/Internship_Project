import argparse

from task1.prompts import DEFAULT_PROMPT
from task1.token_counter import TokenCounter
from task3.semantic_search_day3 import VectorStore
from task3.task3_chat_session import ChatSession, console

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
vector_store = VectorStore()
token_counter = TokenCounter()

vector_store.load_documents()
vector_store.create_doc_embeddings()
while True:
    input_message = input(
        "Please enter your message or enter `/quit` to end your Chat Session: "
    )
    if input_message == "/quit":
        summary = chat.summarize()
        if not summary:
            break
        chat_session = chat.create_logs(token_counter)
        chat.save_logs(chat_session)
        console.print("Logs saved to logs/.", style="bold green")
        break
    console.print(f"[bold green]User:[/bold green] {input_message}")
    query_embedding = vector_store.create_input_embeddings(input_message)
    leader_scores = vector_store.search(query_embedding)
    context = vector_store.create_context(leader_scores)
    query = vector_store.create_query_with_context(input_message, context)
    chat.add_input(query, "user")
    response = chat.send_messages()
    if not response:
        continue
    chat.add_output(response)
    token_counter.count_message(query, response)
