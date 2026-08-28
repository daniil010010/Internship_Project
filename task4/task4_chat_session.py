from openai.types.responses import Response
from rich.console import Console

from task1.chat_session import ChatSession as BaseChatSession
from task1.constants import MODEL
from task1.token_counter import TokenCounter

console = Console()


class ChatSession(BaseChatSession):
    def __init__(self, prompt):
        super().__init__(prompt)

    def send_messages(self) -> None | Response:
        try:
            output = self.client.responses.create(
                model=MODEL, instructions=self.prompt, input=self.messages
            )
        except Exception as error:
            self.handle_error(error)
            self.messages.pop()
            return None

        console.print(f"[bold blue]Assistant:[/bold blue]\n{output.output_text}")
        return output

    def create_logs(self, token_counter: TokenCounter) -> dict:
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
        console.print(
            f"[bold magenta]Total tokens:[/bold magenta] {token_counter.tokens.total}"
        )

        return chat_session
