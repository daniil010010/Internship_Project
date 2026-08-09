from openai import OpenAI
import tiktoken
from datetime import datetime
import json
import os
from dotenv import load_dotenv
from openai import APIConnectionError, APITimeoutError, AuthenticationError, BadRequestError, RateLimitError, APIStatusError
from rich.console import Console
from tools_schemas import tools

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
        self.tool_tokens = {
            "input": 0,
            "output": 0,
            "total": 0
        }
        self.tool_call_history = []


    def send_messages(self):
        try:
            output = self.client.responses.create(
                model=MODEL,
                tools=tools,
                instructions=self.prompt + "\n" + "Use the available tools whenever they can provide a better answer than responding from your own knowledge."
                                                  "\n\nGuidelines:\n- Use 'calculate' for mathematical expressions or calculations.\n- Use 'search_wikipedia' to look up factual information about people, places, events, organizations, scientific concepts, or historical topics."
                                                  "\n- Use 'explain' when the user asks for a simple educational explanation or wants a topic explained in beginner-friendly language.\n- Use 'generate_quiz' when the user requests a quiz or test on a topic."
                                                  "\n\nIf multiple tools are needed to answer the user's request, call all relevant tools before responding.",
                input=self.messages
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
        if output.output_text:
            console.print(f"[bold blue]Assistant:[/bold blue]\n{output.output_text}")
        return output


    def count_tokens(self, message, output, params="", final_count=False):
        encoding = tiktoken.encoding_for_model(MODEL)
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
            self.tokens["input"] += self.tool_tokens["input"]
            self.tokens["output"] += self.tool_tokens["output"]
            self.tokens["total"] += self.tool_tokens["total"]
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
        return summary


    def build_tool_messages(self, message, output):
        tools_messages = [{
            "role": "user",
            "content": message
        }]
        tools_messages += output.output
        return tools_messages


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


    def finish_tool_call(self, tools_messages):
        try:
            response = self.client.responses.create(
                model=MODEL,
                tools=tools,
                instructions=self.prompt + "\n\n" + "You have already received the results from previous tool calls.\n\n"
                                                    "- Do not call the same tool again with the same or similar arguments unless the previous result was insufficient.\n"
                                                    "- Use the available tool outputs whenever possible.\n- Call another tool only if it is required to complete the user's request.\n"
                                                    "- Otherwise provide the final answer.",
                input=tools_messages
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
        console.print(f"[bold blue]Assistant:[/bold blue]\n{response.output_text}")
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


    def save_logs(self, summary):
        chat_session = {
            "timestamp": self.timestamp,
            "prompt": self.prompt,
            "messages": [{
                "role": "system",
                "content": self.prompt
            }],
            "tool_calls": [],
            "tokens": {
                "input": self.tokens["input"],
                "output": self.tokens["output"],
                "total": self.tokens["total"]
            }
        }
        for message in self.messages:
            chat_session["messages"].append(message)
        for tool_call in self.tool_call_history:
            chat_session["tool_calls"].append(tool_call)
        console.print(f"[bold magenta]\nInput tokens:[/bold magenta] {self.tokens['input']}")
        console.print(f"[bold magenta]Output tokens:[/bold magenta] {self.tokens['output']}")
        console.print(f"[bold magenta]Total tokens:[/bold magenta] {self.tokens['total']}")
        if summary:
            chat_session["summary"] = summary.output_text
        log_name = f"logs/{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.json"
        with open(log_name, "w", encoding="utf-8") as f:
            json.dump(chat_session, f, indent=4, ensure_ascii=False)