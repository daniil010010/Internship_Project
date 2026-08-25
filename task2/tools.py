import wikipediaapi
from rich.console import Console

from task1.constants import MODEL

console = Console()

wiki =  wikipediaapi.Wikipedia(user_agent="PythonProject (daniil.chuvurin@gmail.com", language='en')


class Tool:
    def __init__(self, chat_object):
        self.client = chat_object.client
        self.chat_object = chat_object

    def execute(self, name: str, args: dict):
        if name == "calculate":
            return self.calculate(args["expr"])

        if name == "explain":
            return self.explain(args["topic"])

        if name == "generate_quiz":
            return self.generate_quiz(
                args["topic"],
                args["difficulty"]
            )

        if name == "search_wikipedia":
            return self.search_wikipedia(args["query"])

        raise ValueError(f"Unknown tool: {name}")


    def calculate(self, expr: str) -> int | float | None:
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
            console.print("[/bold red]Syntax Error.[/bold red] Incorrect syntax in expression.")
            return None

        return res


    def explain(self, topic: str) -> str | None:
        try:
            explanation = self.client.responses.create(
                model=MODEL,
                instructions="You are an educational assistant. "
                             "Explain the requested study topic in clear, "
                             "beginner-friendly language. Use simple terms, "
                             "avoid unnecessary jargon, and include a short example "
                             "if it improves understanding. Keep the explanation concise.",
                input=topic
            )
        except Exception as error:
            self.chat_object.handle_error(error)
            return None

        return explanation.output_text


    def generate_quiz(self, topic: str, difficulty: str) -> str | None:
        try:
            quiz = self.client.responses.create(
                model=MODEL,
                instructions="You are an experienced teacher. "
                             "Create a short quiz consisting of three questions "
                             "based on the given topic and difficulty level. "
                             "Include the correct answer for each question",
                input=f"Topic: {topic}\nDifficulty: {difficulty}"
            )
        except Exception as error:
            self.chat_object.handle_error(error)
            return None

        return quiz.output_text


    def search_wikipedia(self, query: str) -> str:
        page = wiki.page(query)

        if page.exists():
            summary = page.summary.split(".")
            text = page.title + "\n\n" + ". ".join(summary[:5]) + "."
        else:
            return "No Wikipedia page found."

        return text




