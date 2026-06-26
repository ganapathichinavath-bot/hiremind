import os
import sys
import numpy as np
from pathlib import Path

# Add project root to path to resolve imports
ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from embedder import SklearnEmbedder
from config import ARTIFACTS_DIR

class EmbeddingGenerator:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(EmbeddingGenerator, cls).__new__(cls, *args, **kwargs)
            cls._instance.embedder = None
        return cls._instance
        
    def __init__(self):
        if self.embedder is None:
            try:
                self.embedder = SklearnEmbedder.load(ARTIFACTS_DIR)
                print("Successfully loaded precomputed SklearnEmbedder.")
            except Exception as e:
                print(f"Warning: Could not load precomputed SklearnEmbedder from {ARTIFACTS_DIR}: {e}. Initializing fresh fallback instance.")
                self.embedder = SklearnEmbedder()
                    
    def get_embedding(self, text: str) -> np.ndarray:
        return self.embedder.transform([text])[0]
            
    def get_embeddings(self, texts: list[str]) -> np.ndarray:
        return self.embedder.transform(texts)
