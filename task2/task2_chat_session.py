import json
from datetime import datetime
from pathlib import Path
from task1.constants import MODEL
from task1.chat_session import ChatSession as BaseChatSession

from openai.types.responses import Response
from rich.console import Console

from task2.task2_constants import MAX_TOOL_ITERATIONS
from task2.task2_prompts import BASE_PROMPT, SECOND_PROMPT
from task2.tools_schemas import tools


console = Console()

class ChatSession(BaseChatSession):
    def __init__(self, prompt: str):
        super().__init__(prompt)

        self.tool_call_history = []
        self.token_counter = None
        self.tool = None



    def send_messages(self) -> Response | None:

        try:
            output = self.client.responses.create(
                model=MODEL,
                tools=tools,
                instructions=f"""
                Instructions:
                {BASE_PROMPT}
                
                Additional instructions:
                {self.prompt}
                """,
                input=self.messages)
        except Exception as error:
            print(type(error).__name__, error)
            self.handle_error(error)
            self.messages.pop()
            return None
        if output.output_text:
            console.print(
                f"[bold blue]Assistant:[/bold blue]\n"
                f"{output.output_text}"
            )


        return output

    def add_output(self, output: Response) -> None:
        if output.output_text:
            self.messages.append({
                "role": "assistant",
                "content": output.output_text
            })

    def build_tool_messages(self, message: str, output: Response) -> list:
        tools_messages = [{
            "role": "user",
            "content": message
        }]

        for item in output.output:
            if item.type == "function_call":
                tools_messages.append({
                    "type": "function_call",
                    "call_id": item.call_id,
                    "name": item.name,
                    "arguments": item.arguments
                })

        return tools_messages

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
                    "search_wikipedia"
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


    def add_tool_call(
            self,
            name: str,
            args: dict,
            result: str | float | None
    ) -> None:
        self.tool_call_history.append({
            "type": "tool_call",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "name": name,
            "params": args,
            "result": result
        })


    def finish_tool_call(self, tools_messages: list) -> Response | None:
        try:
            response = self.client.responses.create(
                model=MODEL,
                tools=tools,
                instructions=f"""
                Instructions:
                {SECOND_PROMPT}
                
                Additional instructions:
                {self.prompt}
                """,
                input=tools_messages
            )
        except Exception as error:
            self.handle_error(error)
            return None

        console.print(f"[bold blue]Assistant:[/bold blue]\n{response.output_text}")


        return response


    def contains_tool_call(self, response: Response) -> bool:
        return any(
            item.type == "function_call"
            for item in response.output
        )

    def create_logs(self, summary: str | None) -> None:
        chat_session = {
            "timestamp": self.timestamp,
            "prompt": self.prompt,
            "messages": [{
                "role": "system",
                "content": self.prompt
            }],
            "tool_calls": [],
            "tokens": {
                "input": self.token_counter.tokens.input,
                "output": self.token_counter.tokens.output,
                "total": self.token_counter.tokens.total
            }
        }

        for message in self.messages:
            chat_session["messages"].append(message)
        for tool_call in self.tool_call_history:
            chat_session["tool_calls"].append(tool_call)

        console.print(f"[bold magenta]\nInput tokens:[/bold magenta] {self.token_counter.tokens.input}")
        console.print(f"[bold magenta]Output tokens:[/bold magenta] {self.token_counter.tokens.output}")
        console.print(f"[bold magenta]Total tokens:[/bold magenta] {self.token_counter.tokens.total}")

        if summary:
            chat_session["summary"] = summary.output_text

        return chat_session


    def save_logs(self, chat_session: dict) -> None:
        logs_dir = Path(__file__).resolve().parent / "logs"
        logs_dir.mkdir(exist_ok=True)

        log_name = logs_dir / f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.json"

        with open(log_name, "w", encoding="utf-8") as f:
            json.dump(chat_session, f, indent=4, ensure_ascii=False)

    def process_tool_calls(
            self,
            message: str,
            response: Response
    ) -> Response | None:

        iterations = 0

        while (
                self.contains_tool_call(response)
                and iterations < MAX_TOOL_ITERATIONS
        ):
            tool_messages = self.build_tool_messages(
                message,
                response
            )

            tool_messages = self.run_tools(
                tool_messages,
                message,
                response
            )

            response = self.finish_tool_call(tool_messages)

            if response is None:
                return None

            iterations += 1

        if not self.contains_tool_call(response):
            self.token_counter.count_tokens(
                message,
                response,
                show=False
            )

            self.token_counter.add_tool_tokens()

            console.print(
                f"\n[bold magenta]Tokens used:[/bold magenta] "
                f"{self.token_counter.current_tokens}"
            )

        return response