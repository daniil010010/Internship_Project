from task1.constants import MODEL
from task1.schemas import TokenUsage
from rich.console import Console
import tiktoken

console = Console()

class TokenCounter:
    def __init__(self):
        self.tokens = TokenUsage()

    def count_message(self, message: str, output: str) -> None:
        encoding = tiktoken.encoding_for_model(MODEL)

        self.tokens.input += len(encoding.encode(message))
        self.tokens.output += len(encoding.encode(output))
        self.tokens.total += len(encoding.encode(message)) + len(
            encoding.encode(output)
        )

        console.print(
            f"\n[bold magenta]Tokens used:[/bold magenta] {len(encoding.encode(message)) + len(encoding.encode(output))}"
        )
