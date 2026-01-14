from app.core.vector_db import get_collection
from app.schemas.product import Product
from typing import List
from pydantic import BaseModel

class RAGResult(BaseModel):
    products: List[Product]
    max_similarity: float
    below_threshold: bool

class RAGService:
    def __init__(self, similarity_threshold: float = 0.7):
        self.collection = get_collection()
        self.threshold = similarity_threshold

    async def retrieve(self, query: str, top_k: int = 3) -> RAGResult:
        """
        Query ChromaDB and return products above similarity threshold.
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        products = []
        max_sim = 0.0
        
        if not results['ids'] or not results['ids'][0]:
            return RAGResult(products=[], max_similarity=0.0, below_threshold=True)

        # ChromaDB returns distances. For cosine similarity, distance = 1 - similarity (approx).
        # Actually Chroma defaults to L2, but we set "hnsw:space": "cosine" in get_collection.
        # Cosine distance ranges from 0 (identical) to 2 (opposite).
        # Similarity = 1 - distance.
        
        distances = results['distances'][0]
        metadatas = results['metadatas'][0]
        
        valid_products = []
        
        for i, dist in enumerate(distances):
            similarity = 1 - dist
            max_sim = max(max_sim, similarity)
            
            if similarity >= self.threshold:
                # Convert metadata back to Product
                # Note: We stored simple types in metadata, need to handle Enum conversion if Pydantic doesn't automatically
                try:
                    product = Product.model_validate(metadatas[i])
                    valid_products.append(product)
                except Exception as e:
                    print(f"Error parsing product metadata: {e}")
                    continue

        return RAGResult(
            products=valid_products,
            max_similarity=max_sim,
            below_threshold=len(valid_products) == 0
        )
