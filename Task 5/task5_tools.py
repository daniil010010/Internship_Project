from rich.console import Console
from task5_semantic_search import VectorStore, Embeddings
from task5_chat_session import ChatSession
from pathlib import Path
import wikipediaapi
import sys


console = Console()

wiki =  wikipediaapi.Wikipedia(user_agent="PythonProject (daniil.chuvurin@gmail.com", language='en')


sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent / "Task 2")
)

from tools import Tool as BaseTool



class Tool(BaseTool):
    def __init__(self, store: VectorStore, embeddings: Embeddings, chat: ChatSession) -> None:
        super().__init__()
        self.store = store
        self.embeddings = embeddings
        self.chat = chat


    def semantic_search(
            self,
            query: str,
    ) -> str:
        query_embedding = self.embeddings.create_embedding(query)

        results = self.vector_store.search(
            query_embedding,
            top_k=3
        )

        return self.store.create_context(results)


    def summarize_session(self) -> str:
        return self.chat.summarize()





