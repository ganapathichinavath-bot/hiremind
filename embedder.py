"""High-performance local TF-IDF + SVD embeddings for CPU environments."""

from __future__ import annotations

import pickle
from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD

class SklearnEmbedder:
    """TF-IDF + SVD projection embedder matching sentence-transformers interfaces."""
    def __init__(self) -> None:
        self.vectorizer = TfidfVectorizer(
            max_features=25000,
            stop_words="english",
            ngram_range=(1, 2),
            sublinear_tf=True
        )
        self.svd = TruncatedSVD(n_components=384, random_state=42)
        
        # Pre-fit on dummy text for self-healing fallback use
        dummy_texts = [
            "python fastapi rag vector search embeddings ndcg mrr map evaluation", 
            "ml ai engineer data scientist machine learning deep learning",
            "java spring boot sql consulting enterprise development",
            "computer vision object detection image segmentation",
            "hr recruitment hiring resume match profile"
        ]
        self.vectorizer.fit(dummy_texts)
        self.is_fallback = True

    def fit_transform(self, texts: list[str]) -> np.ndarray:
        print("Fitting TF-IDF Vectorizer...")
        tfidf_matrix = self.vectorizer.fit_transform(texts)
        print("Fitting TruncatedSVD (384 dimensions) projection...")
        embeddings = self.svd.fit_transform(tfidf_matrix)
        
        # L2 normalize embeddings for dot-product cosine similarity
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self.is_fallback = False
        return (embeddings / norms).astype(np.float32)

    def transform(self, texts: list[str]) -> np.ndarray:
        if getattr(self, "is_fallback", False):
            # Fallback when SVD transformer was not loaded: slice/pad TF-IDF representation to 384 dims
            tfidf_matrix = self.vectorizer.transform(texts).toarray()
            vocab_size = tfidf_matrix.shape[1]
            if vocab_size >= 384:
                embeddings = tfidf_matrix[:, :384]
            else:
                embeddings = np.pad(tfidf_matrix, ((0, 0), (0, 384 - vocab_size)), mode='constant')
            
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            return (embeddings / norms).astype(np.float32)
        else:
            tfidf_matrix = self.vectorizer.transform(texts)
            embeddings = self.svd.transform(tfidf_matrix)
            
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            return (embeddings / norms).astype(np.float32)

    def save(self, directory: Path) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        with open(directory / "tfidf_vectorizer.pkl", "wb") as f:
            pickle.dump(self.vectorizer, f)
        with open(directory / "tfidf_svd.pkl", "wb") as f:
            pickle.dump(self.svd, f)

    @classmethod
    def load(cls, directory: Path) -> "SklearnEmbedder":
        embedder = cls.__new__(cls)
        with open(directory / "tfidf_vectorizer.pkl", "rb") as f:
            embedder.vectorizer = pickle.load(f)
        with open(directory / "tfidf_svd.pkl", "rb") as f:
            embedder.svd = pickle.load(f)
        embedder.is_fallback = False
        return embedder
