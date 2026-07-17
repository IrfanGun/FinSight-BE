from functools import lru_cache

from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer("all-MiniLM-L6-v2")


class EmbeddingService:
    def __init__(self):
        self.model = get_embedding_model()

    def embed(self, text: str) -> list[float]:
        return self.model.encode(text).tolist()

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts).tolist()
