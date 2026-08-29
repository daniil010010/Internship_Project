from openai.types.responses import Response
from rich.console import Console

from task1.chat_session import ChatSession as BaseChatSession
from task1.constants import MODEL
from task3.task3_prompts import RAG_PROMPT

console = Console()


class ChatSession(BaseChatSession):
    def __init__(self, prompt: str) -> None:
        super().__init__(prompt)

    def send_messages(self) -> Response | None:
        try:
            output = self.client.responses.create(
                model=MODEL,
                instructions=f"""Instructions
                {RAG_PROMPT}

                Additional instructions
                {self.prompt}
                """,
                input=self.messages,
            )
        except Exception as error:
            self.handle_error(error)
            self.messages.pop()
            return None

        console.print(f"[bold blue]Assistant:[/bold blue]\n{output.output_text}")
        return output.output_text
