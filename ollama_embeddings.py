# ollama_embeddings.py
from langchain.embeddings.base import Embeddings
import requests

class OllamaEmbeddings(Embeddings):
    def __init__(self, endpoint="http://localhost:11434/api/embeddings", model="nomic-embed-text"):
        self.endpoint = endpoint
        self.model = model
        self.session = requests.Session()  # reuse connections

    def embed_query(self, text: str) -> list[float]:
        return self._get_embedding(text)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._get_embedding(text) for text in texts]

    def _get_embedding(self, text: str) -> list[float]:
        payload = {"model": self.model, "prompt": text}
        response = self.session.post(self.endpoint, json=payload)
        response.raise_for_status()
        result = response.json()
        return result["embedding"]
