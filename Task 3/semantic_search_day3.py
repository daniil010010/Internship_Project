from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
from rich.console import Console
import numpy as np
import os

load_dotenv()

console = Console()

API_KEY = os.getenv("API_KEY")

MODEL = "text-embedding-3-small"

class Embeddings:
    def __init__(self):
        self.client = OpenAI(api_key=API_KEY)
        self.documents = {}
        self.embeddings = {}
        self.similarity_scores = {}
        self.leader_scores = None


    def load_documents(self):
        knowledge = Path("knowledge")
        console.print("[bold yellow]System:[/bold yellow]")
        for file in knowledge.glob("*.txt"):
            self.documents[file.name] = file.read_text(encoding="utf-8")
            print(f"Loaded: {file.name}")


    def create_doc_embeddings(self):
        for doc_name, doc in self.documents.items():
            response = self.client.embeddings.create(
                input=doc,
                model=MODEL
            )
            self.embeddings[doc_name] = response.data[0].embedding


    def create_input_embeddings(self, message):
        console.print("[bold yellow]System:[/bold yellow] Creating query embedding")
        response = self.client.embeddings.create(
            input=message,
            model=MODEL
        )
        query_embedding = response.data[0].embedding
        return query_embedding


    def compare_embeddings(self, query_embedding):
        console.print("[bold yellow]System:[/bold yellow] Comparing embeddings")
        for doc_name, embedding in self.embeddings.items():
            cosine_similarity = np.dot(embedding, query_embedding) / (np.linalg.norm(embedding) * np.linalg.norm(query_embedding))
            self.similarity_scores[doc_name] = cosine_similarity


    def sort_scores(self):
        sorted_scores = dict(sorted(self.similarity_scores.items(), key=lambda item: item[1], reverse=True))
        self.leader_scores = {}
        console.print("[bold yellow]System:[/bold yellow] Top 3 matches:")
        for i, (doc_name, score) in enumerate(list(sorted_scores.items())[:3], start=1):
            self.leader_scores[doc_name] = score
            print(f"({i}) {doc_name}")


    def create_context(self):
        console.print("[bold yellow]System:[/bold yellow] Creating context for the query")
        context = "Context:"
        for doc_name in self.leader_scores.keys():
            context += f"\n\nSource: {doc_name}:\n{self.documents[doc_name]}"
        return context


    def create_query_with_context(self, message, context):
        query_with_context = context + "\n\nQuestion:\n" + message
        return query_with_context





