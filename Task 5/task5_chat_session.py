from datetime import datetime
import json
from rich.console import Console
from tools_schemas import tools
from task5_prompts import BASE_PROMPT, TOOL_RESULT_PROMPT
from pathlib import Path
import sys
import os
from openai.types.responses import Response

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent / "Task 2")
)

from task2_chat_sesson import ChatSession as BaseSession


console = Console()

class ChatSession(BaseSession):
    def __init__(self, prompt: str, model: str) -> None:
        super().__init__(prompt)
        self.model = model


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
        for event in stream:
            if event.type == "response.output_text.delta":
                print(event.delta, end="", flush=True)
            elif event.type == "response.completed":
                response = event.response
        print()
        return response


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


    def save_session(self) -> None:
        session = {
            "timestamp": self.timestamp,
            "model": self.model,
            "prompt": self.prompt,
            "messages": self.messages,
            "tokens": self.tokens,
            "tool_calls": self.tool_call_history
        }
        os.makedirs("session", exist_ok=True)
        with open(f"session/{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.json", "w", encoding="utf-8") as f:
            json.dump(session, f, indent=4, ensure_ascii=False, default=str)


    def load_session(self, json_file: str) -> None:
        with open(json_file, "r") as f:
            session = json.load(f)

        self.timestamp = session["timestamp"]
        self.model = session["model"]
        self.prompt = session["prompt"]
        self.messages = session["messages"]
        self.tokens = session["tokens"]
        self.tool_call_history = session.get("tool_calls", [])



