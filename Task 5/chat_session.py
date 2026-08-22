from openai import OpenAI
import tiktoken
from datetime import datetime
import json
import os
from dotenv import load_dotenv
from openai import APIConnectionError, APITimeoutError, AuthenticationError, BadRequestError, RateLimitError, APIStatusError
from rich.console import Console
from tools_schemas import tools
from constants import BASE_PROMPT, TOOL_RESULT_PROMPT

load_dotenv()

API_KEY = os.getenv("API_KEY")

console = Console()

class ChatSession:
    def __init__(self, model, prompt):
        if not API_KEY:
            raise ValueError("API_KEY not set")
        else:
            self.client = OpenAI(api_key=API_KEY)
        self.tokens = {
            "input": 0,
            "output": 0,
            "total": 0
        }
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.model = model
        self.prompt = prompt
        self.messages = []
        self.tool_tokens = {
            "input": 0,
            "output": 0,
            "total": 0
        }
        self.tool_call_history = []
        self.tools_messages = []


    def send_messages_stream(self):
        try:
            stream = self.client.responses.create(
                model=self.model,
                tools=tools,
                instructions=f"{BASE_PROMPT}\n\nAdditional instructions:\n{self.prompt}",
                input=self.messages,
                stream=True
            )
        except APIConnectionError:
            self.messages.pop(-1)
            console.print("[bold red]Connection error.[/bold red] Please check your Internet connection.")
            return None
        except APITimeoutError:
            self.messages.pop(-1)
            console.print("[bold red]Request timed out.[/bold red] Please try again.")
            return None
        except AuthenticationError:
            self.messages.pop(-1)
            console.print("[bold red]Authentication error.[/bold red] Please check your API key.")
            return None
        except BadRequestError:
            self.messages.pop(-1)
            console.print("[bold red]Invalid request.[/bold red] Please check the request parameters.")
            return None
        except RateLimitError:
            self.messages.pop(-1)
            console.print("[bold red]Rate limit exceeded.[/bold red] Please try again later.")
            return None
        except APIStatusError:
            self.messages.pop(-1)
            console.print("[bold red]OpenAI server error.[/bold red] Please try again later.")
            return None
        except Exception as e:
            self.messages.pop(-1)
            console.print(f"[bold red]Unexpected error:[/bold red] {e}")
            return None
        console.print("Assistant is typing...", style="bold blue")
        response=None
        for event in stream:
            if event.type == "response.output_text.delta":
                print(event.delta, end="", flush=True)
            elif event.type == "response.completed":
                response = event.response
        print()
        return response


    def count_tokens(self, message, output, params="", final_count=False):
        encoding = tiktoken.encoding_for_model(self.model)
        if isinstance(message, (dict, list)):
            message = json.dumps(message, default=str)
        input_tokens = len(encoding.encode(message))
        output_tokens = len(encoding.encode(output.output_text))
        for item in output.output:
            if item.type == "function_call":
                self.tool_tokens["input"] += input_tokens
                self.tool_tokens["output"] += len(encoding.encode(f"Function: {item.name}, {params}"))
                self.tool_tokens["total"] += input_tokens + len(encoding.encode(f"Function: {item.name}, {params}"))
                return None
        if final_count:
            self.tokens["input"] += self.tool_tokens["input"] + input_tokens
            self.tokens["output"] += self.tool_tokens["output"] + output_tokens
            self.tokens["total"] += self.tool_tokens["total"] + input_tokens + output_tokens
            console.print(f"\n[bold magenta]Tokens used:[/bold magenta] {self.tool_tokens['total']}")
        else:
            self.tokens["input"] += input_tokens
            self.tokens["output"] += output_tokens
            self.tokens["total"] += input_tokens + output_tokens
            console.print(f"\n[bold magenta]Tokens used:[/bold magenta] {input_tokens + output_tokens}")


    def add_input(self, message, role):
        self.messages.append({
            "role": role,
            "content": message
        })


    def add_output(self, output):
        for item in output.output:
            if item.type == "function_call":
                console.print(f"[bold blue]Assistant:[/bold blue] function_call({item.name})")
        if output.output_text:
            self.messages.append({
                "role": "assistant",
                "content": output.output_text
            })


    def summarize(self):
        try:
            summary = self.client.responses.create(
                model=self.model,
                instructions="Provide a short summary of this conversation",
                input=self.messages)
        except APIConnectionError:
            console.print("[bold red]Connection error.[/bold red] Please check your Internet connection.")
            return None
        except APITimeoutError:
            console.print("[bold red]Request timed out.[/bold red] Please try again.")
            return None
        except AuthenticationError:
            console.print("[bold red]Authentication error.[/bold red] Please check your API key.")
            return None
        except BadRequestError:
            console.print("[bold red]Invalid request.[/bold red] Please check the request parameters.")
            return None
        except RateLimitError:
            console.print("[bold red]Rate limit exceeded.[/bold red] Please try again later.")
            return None
        except APIStatusError:
            console.print("[bold red]OpenAI server error.[/bold red] Please try again later.")
            return None
        except Exception as e:
            console.print(f"[bold red]Unexpected error:[/bold red] {e}")
            return None
        console.print(f"[bold yellow]Conversation Summary[/bold yellow]\n[bold blue]Assistant:[/bold blue] {summary.output_text}")
        return summary


    def build_tool_messages(self, message, output):
        if not self.tools_messages:
            self.tools_messages.append({
                "role": "user",
                "content": message
            })

        self.tools_messages.extend(output.output)

        return self.tools_messages


    def run_tools(self, tools_messages, message, output, tool):
        for item in output.output:
            if item.type == "function_call":
                tool_params = {}
                args = json.loads(item.arguments)
                self.tool_activation = True
                if item.name == "calculate":
                    res = tool.calculate(args["expr"])
                    tool_params["expr"] = args["expr"]
                    result = res
                elif item.name == "explain":
                    explanation = tool.explain(args["topic"])
                    tool_params["topic"] = args["topic"]
                    result = explanation
                elif item.name == "generate_quiz":
                    quiz = tool.generate_quiz(args["topic"], args["difficulty"])
                    tool_params["topic"] = args["topic"]
                    tool_params["difficulty"] = args["difficulty"]
                    result = quiz
                elif item.name == "search_wikipedia":
                    lookup = tool.search_wikipedia(args["query"])
                    tool_params["query"] = args["query"]
                    result = lookup
                elif item.name == "summarize_session":
                    summary = tool.summarize_session()
                    result = summary
                elif item.name == "semantic_search":
                    search_result = tool.semantic_search(args["query"])
                    tool_params["query"] = args["query"]
                    result = search_result
                if item.name != "explain" and item.name != "generate_quiz" and item.name != "search_wikipedia":
                    console.print(f"[bold blue]Result:[/bold blue] {result}")
                formatted_params = ", ".join(f"{k}={v}" for k, v in tool_params.items())
                self.count_tokens(message=message, output=output, params=formatted_params)
                self.add_tool_call(item.name, args, result)
                tools_messages.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": "" if result is None else str(result)
                })
        return tools_messages


    def add_tool_call(self, name, args, result):
        self.tool_call_history.append({
            "type": "tool_call",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "name": name,
            "params": args,
            "result": result
        })


    def finish_tool_call_stream(self, tools_messages):
        try:
            stream = self.client.responses.create(
                model=self.model,
                tools=tools,
                instructions=f"{BASE_PROMPT}\n\nAdditional instructions:\n{self.prompt}\n\n{TOOL_RESULT_PROMPT}",
                input=tools_messages,
                stream=True
            )
        except APIConnectionError:
            console.print("[bold red]Connection error.[/bold red] Please check your Internet connection.")
            return None
        except APITimeoutError:
            console.print("[bold red]Request timed out.[/bold red] Please try again.")
            return None
        except AuthenticationError:
            console.print("[bold red]Authentication error.[/bold red] Please check your API key.")
            return None
        except BadRequestError:
            console.print("[bold red]Invalid request.[/bold red] Please check the request parameters.")
            return None
        except RateLimitError:
            console.print("[bold red]Rate limit exceeded.[/bold red] Please try again later.")
            return None
        except APIStatusError:
            console.print("[bold red]OpenAI server error.[/bold red] Please try again later.")
            return None
        except Exception as e:
            console.print(f"[bold red]Unexpected error:[/bold red] {e}")
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


    def clear_tool(self):
        self.tool_tokens = {
            "input": 0,
            "output": 0,
            "total": 0
        }


    def contains_tool_call(self, response):
        for item in response.output:
            if item.type == "function_call":
                return True
        return False


    def save_session(self):
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


    def load_session(self, json_file):
        with open(json_file, "r") as f:
            session = json.load(f)

        self.timestamp = session["timestamp"]
        self.model = session["model"]
        self.prompt = session["prompt"]
        self.messages = session["messages"]
        self.tokens = session["tokens"]
        self.tool_call_history = session.get("tool_calls", [])

