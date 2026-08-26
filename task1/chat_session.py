import json
from datetime import datetime

import tiktoken
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    OpenAI,
    RateLimitError,
)
from openai.types.responses import Response
from rich.console import Console

from task1.config import API_KEY
from task1.constants import MODEL
from task1.prompts import SUMMARY_PROMPT
from task1.token_counter import TokenCounter

console = Console()


class ChatSession:
    def __init__(self, prompt: str):
        self.client = OpenAI(api_key=API_KEY)
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.prompt = prompt
        self.messages = []

    def send_messages(self) -> str | None:
        try:
            stream = self.client.responses.create(
                model=MODEL, instructions=self.prompt, input=self.messages, stream=True
            )
        except Exception as error:
            self.handle_error(error)
            self.messages.pop()
            return None

        console.print("Assistant is typing...", style="bold blue")

        output_parts = []

        for event in stream:
            if event.type == "response.output_text.delta":
                output_parts.append(event.delta)
                print(event.delta, end="", flush=True)
        output = "".join(output_parts)

        return output

    def add_input(self, message: str, role: str) -> None:
        self.messages.append({"role": role, "content": message})

    def add_output(self, output: str) -> None:
        self.messages.append({"role": "assistant", "content": output})

    def summarize(self) -> Response | None:
        try:
            summary = self.client.responses.create(
                model=MODEL, instructions=SUMMARY_PROMPT, input=self.messages
            )
        except Exception as error:
            self.handle_error(error)
            return None

        console.print(
            f"[bold yellow]Conversation Summary[/bold yellow]\n[bold blue]Assistant:[/bold blue] {summary.output_text}"
        )

        return summary

    def create_logs(self, token_counter: TokenCounter) -> dict:
        summary = self.summarize()
        chat_session = {
            "timestamp": self.timestamp,
            "prompt": self.prompt,
            "messages": [{"role": "system", "content": self.prompt}],
            "tokens": {
                "input": token_counter.tokens.input,
                "output": token_counter.tokens.output,
                "total": token_counter.tokens.total,
            },
        }

        for message in self.messages:
            chat_session["messages"].append(message)
        console.print(f"[bold magenta]Total tokens:[/bold magenta] {token_counter.tokens.total}")
        if summary:
            chat_session["summary"] = summary.output_text
        return chat_session

    def save_logs(self, chat_session: dict) -> None:
        log_name = f"logs/{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.json"
        with open(log_name, "w", encoding="utf-8") as f:
            json.dump(chat_session, f, indent=4, ensure_ascii=False)

    def handle_error(self, error: Exception) -> None:
        if isinstance(error, APIConnectionError):
            console.print(
                "[bold red]Connection error.[/bold red] "
                "Please check your Internet connection."
            )
        elif isinstance(error, APITimeoutError):
            console.print("[bold red]Request timed out.[/bold red] Please try again.")
        elif isinstance(error, AuthenticationError):
            console.print(
                "[bold red]Authentication error.[/bold red] Please check your API key."
            )
        elif isinstance(error, BadRequestError):
            console.print(
                "[bold red]Invalid request.[/bold red] "
                "Please check the request parameters."
            )
        elif isinstance(error, RateLimitError):
            console.print(
                "[bold red]Rate limit exceeded.[/bold red] Please try again later."
            )
        elif isinstance(error, APIStatusError):
            console.print(
                "[bold red]OpenAI server error.[/bold red] Please try again later."
            )
        else:
            console.print("[bold red]Unexpected error:[/bold red]")
