from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
from rich.console import Console
from constants import EMBEDDING_MODEL
import numpy as np
import os

load_dotenv()

console = Console()

API_KEY = os.getenv("API_KEY")

class Embeddings:
    def __init__(self):
        self.client = OpenAI(api_key=API_KEY)


    def create_doc_embeddings(self, docs):
        embeddings = {}
        for doc_name, text in docs.items():
            embeddings[doc_name] = self.create_embedding(text)
        return embeddings


    def create_embedding(self, message):
        console.print("[bold yellow]System:[/bold yellow] Creating query embedding")
        response = self.client.embeddings.create(
            input=message,
            model=EMBEDDING_MODEL
        )
        return response.data[0].embedding



class VectorStore:
    def __init__(self):
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


    def build_index(self, embeddings):
        self.embeddings = embeddings.create_doc_embeddings(self.documents)


    def compare_embeddings(self, query_embedding):
        self.similarity_scores = {}
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


    def create_query_with_context(self, message):
        context = []
        console.print("[bold yellow]System:[/bold yellow] Creating context for the query")
        for doc_name in self.leader_scores.keys():
            context.append(f"\n\nSource: {doc_name}:\n{self.documents[doc_name]}")
        return f"""Context:
        {'\n\n'.join(context)}
        
        Question:
        {message}
        """


    def add_document(self, text, embeddings, file_name):
        self.documents[file_name] = text
        embedding = embeddings.create_embedding(text)
        self.embeddings[file_name] = embedding


    def search(self, message, embeddings):
        query_embedding = embeddings.create_embedding(message)
        self.compare_embeddings(query_embedding)
        self.sort_scores()
        return self.create_query_with_context(message)













