from openai import OpenAI
import tiktoken
from datetime import datetime
import json
import os
from dotenv import load_dotenv
from openai import APIConnectionError, APITimeoutError, AuthenticationError, BadRequestError, RateLimitError, APIStatusError
from rich.console import Console

load_dotenv()

API_KEY = os.getenv("API_KEY")

console = Console()

MODEL = "gpt-5"

class ChatSession:
    def __init__(self, prompt):
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
        self.prompt = prompt
        self.messages = []


    def send_messages(self, role, message):
        self.add_input(message, role)
        try:
            stream = self.client.responses.create(
                model=MODEL,
                instructions=self.prompt,
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
        output = []
        for event in stream:
            if event.type == "response.output_text.delta":
                output.append(event.delta)
                print(event.delta, end="", flush=True)
        output = "".join(output)
        self.add_output(output)
        self.count_tokens(message, output)
        return output


    def count_tokens(self, message, output):
        encoding = tiktoken.encoding_for_model(MODEL)
        self.tokens["input"] += len(encoding.encode(message))
        self.tokens["output"] += len(encoding.encode(output))
        self.tokens["total"] += (len(encoding.encode(message)) + len(encoding.encode(output)))
        console.print(f"\n[bold magenta]Tokens used:[/bold magenta] {len(encoding.encode(message)) + len(encoding.encode(output))}")


    def add_input(self, message, role):
        self.messages.append({
            "role": role,
            "content": message
        })


    def add_output(self, output):
        self.messages.append({
            "role": "assistant",
            "content": output
        })


    def summarize(self):
        try:
            summary = self.client.responses.create(
                model=MODEL,
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
        return summary.output_text


    def save_logs(self):
        summary = self.summarize()
        chat_session = {}
        chat_session["timestamp"] = self.timestamp
        chat_session["prompt"] = self.prompt
        chat_session["messages"] = []
        chat_session["messages"].append({
            "role": "system",
            "content": self.prompt
        })
        for message in self.messages:
            chat_session["messages"].append(message)
        chat_session["tokens"] = {}
        chat_session["tokens"]["input"] = self.tokens["input"]
        console.print(f"[bold magenta]Input tokens:[/bold magenta] {self.tokens['input']}")
        chat_session["tokens"]["output"] = self.tokens["output"]
        console.print(f"[bold magenta]Output tokens:[/bold magenta] {self.tokens['output']}")
        chat_session["tokens"]["total"] = self.tokens["total"]
        console.print(f"[bold magenta]Total tokens:[/bold magenta] {self.tokens['total']}")
        if summary:
            chat_session["summary"] = summary
        log_name = f"logs/{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.json"
        with open(log_name, "w", encoding="utf-8") as f:
            json.dump(chat_session, f, indent=4, ensure_ascii=False)