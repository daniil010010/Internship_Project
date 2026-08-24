from openai import OpenAI
from pathlib import Path
from rich.console import Console
from task5_constants import EMBEDDING_MODEL
import numpy as np
import sys
import faiss


console = Console()



sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent / "Task 3")
)


from semantic_search_day3 import VectorStore as BaseVectorStore


sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent / "Task 1")
)

from config import API_KEY


class Embeddings:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=API_KEY)

    def create_doc_embeddings(
            self,
            docs: dict[str, str]
    ) -> dict[str, list[float]]:
        embeddings = {}

        for doc_name, text in docs.items():
            embeddings[doc_name] = self.create_embedding(text)

        return embeddings


    def create_embedding(self, text: str):
        console.print("[bold yellow]System:[/bold yellow] Creating query embedding")
        response = self.client.embeddings.create(
            input=text,
            model=EMBEDDING_MODEL
        )
        return response.data[0].embedding



class VectorStore(BaseVectorStore):
    def __init__(self):
        super().__init__()


    def build_index(
            self,
            embeddings: dict[str, list[float]]
    ) -> None:
        self.document_names = list(embeddings.keys())

        vectors = np.array(
            list(embeddings.values()),
            dtype="float32"
        )

        faiss.normalize_L2(vectors)

        dimension = vectors.shape[1]

        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(vectors)


    def search(
            self,
            query_embedding: list[float],
            top_k: int = 3
    ) -> dict[str, float]:

        if self.index is None:
            raise RuntimeError("FAISS index is not initialized")

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

        return results


    def add_document(self,
                     text: str,
                     embeddings: Embeddings,
                     file_name: str
    ) -> None:
        self.documents[file_name] = text
        embedding = embeddings.create_embedding(text)
        self.embeddings[file_name] = embedding













