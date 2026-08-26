from openai import OpenAI
from pathlib import Path
from rich.console import Console
import sys
import faiss
import numpy as np
from task3_constants import EMBEDDING_MODEL


sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent / "Task 1")
)

from config import API_KEY


console = Console()




class VectorStore:
    def __init__(self):
        self.client = OpenAI(api_key=API_KEY)
        self.documents: dict[str, str] = {}
        self.document_names: list[str] = []
        self.index: faiss.Index | None = None

    def load_documents(self) -> None:
        knowledge = Path("knowledge")

        console.print("[bold yellow]System:[/bold yellow]")

        for file in knowledge.glob("*.txt"):
            self.documents[file.name] = file.read_text(
                encoding="utf-8"
            )

            print(f"Loaded: {file.name}")

    def create_doc_embeddings(self) -> None:
        embeddings: list[list[float]] = []

        self.document_names.clear()

        for doc_name, doc in self.documents.items():
            response = self.client.embeddings.create(
                input=doc,
                model=EMBEDDING_MODEL
            )

            embeddings.append(response.data[0].embedding)
            self.document_names.append(doc_name)

        vectors = np.array(
            embeddings,
            dtype="float32"
        )

        faiss.normalize_L2(vectors)

        dimension = vectors.shape[1]

        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(vectors)

    def create_input_embeddings(
            self,
            message: str
    ) -> list[float]:
        console.print(
            "[bold yellow]System:[/bold yellow] "
            "Creating query embedding"
        )

        response = self.client.embeddings.create(
            input=message,
            model=EMBEDDING_MODEL
        )

        return response.data[0].embedding


    def search(
            self,
            query_embedding: list[float],
            top_k: int = 3
    ) -> dict[str, float]:

        if self.index is None:
            raise RuntimeError("FAISS index is not initialized")

        console.print(
            "[bold yellow]System:[/bold yellow] "
            "Comparing embeddings"
        )

        query = np.array(
            [query_embedding],
            dtype="float32"
        )

        faiss.normalize_L2(query)

        scores, indices = self.index.search(
            query,
            top_k
        )

        results = {}

        for score, index in zip(scores[0], indices[0]):
            doc_name = self.document_names[index]

            results[doc_name] = float(score)

        console.print(
            "[bold yellow]System:[/bold yellow] Top 3 matches:"
        )

        for i, (doc_name, score) in enumerate(results.items(), start=1):
            console.print(
                f"({i}) {doc_name}: {score}"
            )

        return results



    def create_context(self, leader_scores: dict) -> str:
        console.print(
            "[bold yellow]System:[/bold yellow] "
            "Creating context for the query"
        )

        context = "Context:"

        for doc_name in leader_scores:
            context += (
                f"\n\nSource: {doc_name}:\n"
                f"{self.documents[doc_name]}"
            )

        return context


    def create_query_with_context(
            self,
            message: str,
            context: str
    ) -> str:
        query_with_context = context + "\n\nQuestion:\n" + message
        return query_with_context





