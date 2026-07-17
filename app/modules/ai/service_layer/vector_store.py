import chromadb  # type: ignore[import]

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_or_create_collection(name="finance_records")

    def add_document(
            self,
            documents: list[str],
            embeddings: list[list[float]],
            ids: list[str]
    ):
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            ids=ids
        )
    
    def search (self, query_embedding: list[float], n_results: int = 5) -> list[dict]:
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        documents = results["documents"][0]
        distances = results["distances"][0]

        return [
            {
                "document": doc,
                "distance": dist
            }
            for doc, dist in zip(documents, distances)
        ]

