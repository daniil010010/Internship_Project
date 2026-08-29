from rich.console import Console

from task2.tools import Tool as BaseTool
from task5.task5_chat_session import ChatSession
from task5.task5_semantic_search import Embeddings, VectorStore


console = Console()

class Tool(BaseTool):
    def __init__(self, store: VectorStore, embeddings: Embeddings, chat_object: ChatSession) -> None:
        super().__init__(chat_object)
        self.store = store
        self.embeddings = embeddings

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

        if name == "semantic_search":
            return self.semantic_search(args["query"])

        if name == "summarize_session":
            return self.summarize_session()

        raise ValueError(f"Unknown tool: {name}")


    def semantic_search(
            self,
            query: str,
    ) -> str:
        query_embedding = self.embeddings.create_embedding(query)

        results = self.store.search(
            query_embedding,
            top_k=3
        )

        return self.store.create_context(results)


    def summarize_session(self) -> str:
        return self.chat_object.summarize()





