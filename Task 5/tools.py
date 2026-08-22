from openai import OpenAI
from dotenv import load_dotenv
from chat_session import MODEL
from rich.console import Console
from openai import APIConnectionError, APITimeoutError, AuthenticationError, BadRequestError, RateLimitError, APIStatusError
import os
import wikipediaapi

load_dotenv()

console = Console()

wiki =  wikipediaapi.Wikipedia(user_agent="PythonProject (daniil.chuvurin@gmail.com", language='en')

API_KEY = os.getenv("API_KEY")

class Tool:
    def __init__(self, store, embeddings, chat):
        self.client = OpenAI(api_key=API_KEY)
        self.store = store
        self.embeddings = embeddings
        self.chat = chat

    def calculate(self, expr):
        try:
            nums = set("0123456789+-*/(). ")
            for num in expr:
                if num not in nums:
                    raise ValueError
            res = eval(expr)
        except ValueError:
            console.print("[bold red]Value error.[/bold red] The expression contains unsupported characters.")
            return None
        except ZeroDivisionError:
            console.print("[bold red]Zero Division Error.[/bold red] Can't be divided by 0.")
            return None
        except SyntaxError:
            console.print("[bold red]Syntax Error.[/bold red] Incorrect syntax in expression.")
            return None
        return res


    def explain(self, topic):
        try:
            explanation = self.client.responses.create(
                model=MODEL,
                instructions="You are an educational assistant. Explain the requested study topic in clear, beginner-friendly language. Use simple terms, avoid unnecessary jargon, and include a short example if it improves understanding. Keep the explanation concise.",
                input=topic
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
        return explanation.output_text


    def generate_quiz(self, topic, difficulty):
        try:
            quiz = self.client.responses.create(
                model=MODEL,
                instructions="You are an experienced teacher. Create a short quiz consisting of three questions based on the given topic and difficulty level. Include the correct answer for each question",
                input=f"Topic: {topic}\nDifficulty: {difficulty}"
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
        return quiz.output_text


    def search_wikipedia(self, query):
        page = wiki.page(query)
        if page.exists():
            summary = page.summary.split(".")
            text = page.title + "\n\n" + ". ".join(summary[:5]) + "."
        else:
            return "No Wikipedia page found."
        return text


    def semantic_search(self, query):
        return self.store.search(query, self.embeddings)

    def summarize_session(self):
        return self.chat.summarize()





