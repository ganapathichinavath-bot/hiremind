import chromadb
from chromadb.config import Settings
import os
from typing import List, Dict, Any

class ChromaStore:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ChromaStore, cls).__new__(cls, *args, **kwargs)
            cls._instance.client = None
            cls._instance.collection = None
        return cls._instance

    def __init__(self):
        if self.client is None:
            persist_dir = os.path.join(os.getcwd(), "chroma_db")
            os.makedirs(persist_dir, exist_ok=True)
            self.client = chromadb.PersistentClient(path=persist_dir)
            # Create or get collection
            self.collection = self.client.get_or_create_collection(
                name="candidates",
                metadata={"hnsw:space": "cosine"}
            )

    def add_candidates(self, ids: List[str], embeddings: List[List[float]], metadatas: List[Dict[str, Any]]):
        # Convert any non-simple types in metadata to string for ChromaDB compatibility
        clean_metadatas = []
        for meta in metadatas:
            clean_meta = {}
            for k, v in meta.items():
                if isinstance(v, (str, int, float, bool)):
                    clean_meta[k] = v
                elif v is None:
                    clean_meta[k] = ""
                else:
                    clean_meta[k] = str(v)
            clean_metadatas.append(clean_meta)

        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            metadatas=clean_metadatas
        )

    def query_candidates(self, query_embedding: List[float], top_k: int = 100) -> List[Dict[str, Any]]:
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        parsed_results = []
        if results and "ids" in results and len(results["ids"]) > 0:
            ids = results["ids"][0]
            distances = results["distances"][0] if "distances" in results else [0.0] * len(ids)
            metadatas = results["metadatas"][0] if "metadatas" in results else [{}] * len(ids)
            
            for idx, cid in enumerate(ids):
                # Cosine distance to similarity: 1 - distance
                similarity = 1.0 - distances[idx]
                parsed_results.append({
                    "candidate_id": cid,
                    "similarity": float(similarity),
                    "metadata": metadatas[idx]
                })
        return parsed_results

    def delete_all(self):
        self.client.delete_collection("candidates")
        self.collection = self.client.create_collection("candidates", metadata={"hnsw:space": "cosine"})
