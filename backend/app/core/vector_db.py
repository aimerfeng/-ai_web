import chromadb
from chromadb.config import Settings
from app.core.config import settings

def get_chroma_client():
    """Get ChromaDB client."""
    return chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIRECTORY)

def get_collection():
    """Get or create the product collection."""
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=settings.CHROMA_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )
