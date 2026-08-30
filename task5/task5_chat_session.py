import json
from pathlib import Path
from datetime import datetime

from openai.types.responses import Response
from rich.console import Console

from task2.task2_chat_session import ChatSession as BaseSession
from task5.task5_prompts import BASE_PROMPT, TOOL_RESULT_PROMPT, SEARCH_PROMPT, SUMMARY_PROMPT
from task5.tools_schemas import tools


console = Console()

class ChatSession(BaseSession):
    def __init__(self, prompt: str, model: str) -> None:
        super().__init__(prompt)
        self.model = model
        self.commands = []

    def send_search_messages(self) -> Response | None:
        try:
            output = self.client.responses.create(
                model=self.model,
                instructions=f"""{BASE_PROMPT}\n\n
                {SEARCH_PROMPT}\n\n
                Additional instructions:\n{self.prompt}""",
                input=self.messages,
            )
        except Exception as error:
            self.handle_error(error)
            self.messages.pop()
            return None

        console.print("Assistant:", style="bold blue")
        print(output.output_text)
        return output



    def send_messages_stream(self) -> Response | None:
        try:
            stream = self.client.responses.create(
                model=self.model,
                tools=tools,
                instructions=f"{BASE_PROMPT}\n\nAdditional instructions:\n{self.prompt}",
                input=self.messages,
                stream=True
            )
        except Exception as error:
            self.handle_error(error)
            self.messages.pop()
            return None
        response=None
        console.print("Assistant:", style="bold blue")
        for event in stream:
            if event.type == "response.output_text.delta":
                print(event.delta, end="", flush=True)
            elif event.type == "response.completed":
                response = event.response
        print()
        return response

    def run_tools(
            self,
            tools_messages: list,
            message: str,
            output: Response
    ) -> list:

        for item in output.output:
            if item.type == "function_call":
                args = json.loads(item.arguments)

                console.print(
                    f"[bold blue]Assistant:[/bold blue] "
                    f"function_call({item.name})"
                )

                result = self.tool.execute(item.name, args)

                if item.name not in {
                    "explain",
                    "generate_quiz",
                    "search_wikipedia",
                    "summarize_session"
                }:
                    console.print(
                        f"[bold blue]Result:[/bold blue] {result}"
                    )

                formatted_params = ", ".join(
                    f"{k}={v}" for k, v in args.items()
                )

                self.token_counter.count_tool_tokens(
                    message=message,
                    output=output,
                    params=formatted_params
                )

                self.add_tool_call(
                    item.name,
                    args,
                    result
                )

                tools_messages.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": "" if result is None else str(result)
                })

        return tools_messages

    def finish_tool_call_stream(self, tools_messages: list) -> Response | None:
        try:
            stream = self.client.responses.create(
                model=self.model,
                tools=tools,
                instructions=f"{BASE_PROMPT}\n\nAdditional instructions:\n{self.prompt}\n\n{TOOL_RESULT_PROMPT}",
                input=tools_messages,
                stream=True
            )
        except Exception as error:
            self.handle_error(error)
            return None
        console.print("Assistant is typing...", style="bold blue")
        response = None
        for event in stream:
            if event.type == "response.output_text.delta":
                print(event.delta, end="", flush=True)
            elif event.type == "response.completed":
                response = event.response
        print()
        return response

    def summarize(self) -> Response | None:
        try:
            summary = self.client.responses.create(
                model=self.model,
                instructions=SUMMARY_PROMPT,
                input=self.messages
            )
        except Exception as error:
            self.handle_error(error)
            return None

        console.print(
            f"[bold yellow]Conversation Summary[/bold yellow]\n[bold blue]Assistant:[/bold blue] {summary.output_text}"
        )

        return summary.output_text

    def add_command(self, command: str, **kwargs) -> None:
        self.commands.append({
            "command": command,
            **kwargs
        })


    def save_session(self) -> None:
        session = {
            "timestamp": self.timestamp,
            "model": self.model,
            "prompt": self.prompt,
            "messages": self.messages,
            "tokens": self.token_counter.tokens,
            "tool_calls": self.tool_call_history,
            "commands": self.commands
        }
        session_dir = Path(__file__).resolve().parent / "session"
        session_dir.mkdir(exist_ok=True)

        session_file = session_dir / (
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.json"
        )

        with open(
                session_file,
                "w",
                encoding="utf-8"
        ) as f:
            json.dump(session, f, indent=4, ensure_ascii=False, default=str)

        console.print(f"Session saved to {session_file}", style="bold green")


    def load_session(self, json_file: str) -> None:
        with open(json_file, "r") as f:
            session = json.load(f)

        self.timestamp = session["timestamp"]
        self.model = session["model"]
        self.prompt = session["prompt"]
        self.messages = session["messages"]
        self.tokens = session["tokens"]
        self.tool_call_history = session.get("tool_calls", [])
        self.commands = session["commands"]



