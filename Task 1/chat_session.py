from openai import OpenAI
import tiktoken
from datetime import datetime
import json
from openai import (APIConnectionError,
                    APITimeoutError,
                    AuthenticationError,
                    BadRequestError,
                    RateLimitError,
                    APIStatusError)
from rich.console import Console
from pydantic_settings import BaseSettings, SettingsConfigDict, BaseModel

from constants import MODEL
from prompts import SUMMARY_PROMPT


class Settings(BaseSettings):
    api_key: str

    model_config = SettingsConfigDict(env_file=".env")


class TokenUsage(BaseModel):
    input: int = 0
    output: int = 0
    total: int = 0


settings = Settings()

API_KEY = settings.api_key

console = Console()

class ChatSession:
    def __init__(self, prompt: str):
        if not API_KEY:
            raise ValueError("API_KEY not set")

        self.client = OpenAI(api_key=API_KEY)
        self.tokens = TokenUsage()
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.prompt = prompt
        self.messages = []


    def send_messages(self, role: str, message: str) -> str | None:
        self.add_input(message, role)

        try:
            stream = self.client.responses.create(
                model=MODEL,
                instructions=self.prompt,
                input=self.messages,
                stream=True
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

        self.add_output(output)
        self.count_tokens(message, output)

        return output


    def count_tokens(self, message: str, output: str) -> None:
        encoding = tiktoken.encoding_for_model(MODEL)

        self.tokens.input += len(encoding.encode(message))
        self.tokens.output += len(encoding.encode(output))
        self.tokens.total += (len(encoding.encode(message)) + len(encoding.encode(output)))

        console.print(f"\n[bold magenta]Tokens used:[/bold magenta] {len(encoding.encode(message)) + len(encoding.encode(output))}")


    def add_input(self, message: str, role: str) -> None:
        self.messages.append({
            "role": role,
            "content": message
        })


    def add_output(self, output: str) -> None:
        self.messages.append({
            "role": "assistant",
            "content": output
        })


    def summarize(self) -> str | None:
        try:

            summary = self.client.responses.create(
                model=MODEL,
                instructions=SUMMARY_PROMPT,
                input=self.messages)
        except Exception as error:
            self.handle_error(error)
            return None

        console.print(f"[bold yellow]Conversation Summary[/bold yellow]\n[bold blue]Assistant:[/bold blue] {summary.output_text}")

        return summary.output_text


    def create_logs(self) -> dict:
        summary = self.summarize()
        chat_session = {
            "timestamp": self.timestamp,
            "prompt": self.prompt,
            "messages": [{
                "role": "system",
                "content": self.prompt
            }],
            "tokens": {
                "input": self.tokens.input,
                "output": self.tokens.output,
                "total": self.tokens.total
            }
        }

        for message in self.messages:
            chat_session["messages"].append(message)
        console.print(f"[bold magenta]Total tokens:[/bold magenta] {self.tokens.total}")
        if summary:
            chat_session["summary"] = summary
        return chat_session


    def save_logs(self, chat_session: dict) -> None:
        log_name = f"logs/{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.json"
        with open(log_name, "w", encoding="utf-8") as f:
            json.dump(chat_session, f, indent=4, ensure_ascii=False)


    def handle_error(self, error: Exception) -> None:
        if isinstance(error, APIConnectionError):
            console.print("[bold red]Connection error.[/bold red] "
                          "Please check your Internet connection.")
        elif isinstance(error, APITimeoutError):
            console.print("[bold red]Request timed out.[/bold red] "
                          "Please try again.")
        elif isinstance(error, AuthenticationError):
            console.print("[bold red]Authentication error.[/bold red] "
                          "Please check your API key.")
        elif isinstance(error, BadRequestError):
            console.print("[bold red]Invalid request.[/bold red] "
                          "Please check the request parameters.")
        elif isinstance(error, RateLimitError):
            console.print("[bold red]Rate limit exceeded.[/bold red] "
                          "Please try again later.")
        elif isinstance(error, APIStatusError):
            console.print("[bold red]OpenAI server error.[/bold red] "
                          "Please try again later.")
        else:
            console.print("[bold red]Unexpected error:[/bold red]")





