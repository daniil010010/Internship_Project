import json

import tiktoken
from openai.types.responses import Response
from rich.console import Console

from task1.constants import MODEL
from task1.token_counter import TokenCounter as BaseTokenCounter
from task2.task2_schemas import ToolTokenUsage

console = Console()

class TokenCounter(BaseTokenCounter):
    def __init__(self):
        super().__init__()
        self.tool_tokens = ToolTokenUsage()
        self.current_tokens = 0


    def count_tokens(
            self,
            message: str | dict | list,
            output: Response,
            show: bool = False,
    ) -> None:
        encoding = tiktoken.encoding_for_model(MODEL)

        if isinstance(message, (dict, list)):
            message = json.dumps(message, default=str)

        input_tokens = len(encoding.encode(str(message)))
        output_tokens = len(encoding.encode(output.output_text))

        current_tokens = input_tokens + output_tokens

        self.current_tokens += current_tokens

        self.tokens.input += input_tokens
        self.tokens.output += output_tokens
        self.tokens.total += current_tokens

        if show:
            console.print(
                f"\n[bold magenta]Tokens used:[/bold magenta] "
                f"{input_tokens + output_tokens}"
            )

    def count_tool_tokens(
            self,
            message: str | dict | list,
            output: Response,
            params: str
    ) -> None:
        encoding = tiktoken.encoding_for_model(MODEL)

        if isinstance(message, (dict, list)):
            message = json.dumps(message, default=str)

        input_tokens = len(encoding.encode(str(message)))

        for item in output.output:
            if item.type == "function_call":
                function_tokens = len(
                    encoding.encode(
                        f"Function: {item.name}, {params}"
                    )
                )

                self.tool_tokens.input += input_tokens
                self.tool_tokens.output += function_tokens
                self.tool_tokens.total += (
                        input_tokens + function_tokens
                )


    def add_tool_tokens(self) -> None:
        self.current_tokens += self.tool_tokens.total

        self.tokens.input += self.tool_tokens.input
        self.tokens.output += self.tool_tokens.output
        self.tokens.total += self.tool_tokens.total

    def reset_tool_tokens(self) -> None:
        self.current_tokens = 0
        self.tool_tokens.input = 0
        self.tool_tokens.output = 0
        self.tool_tokens.total = 0

    def get_current_tokens(self) -> int:
        return self.tool_tokens.total + self.current_tokens