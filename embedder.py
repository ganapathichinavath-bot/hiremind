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

    def fit_transform(self, texts: list[str]) -> np.ndarray:
        print("Fitting TF-IDF Vectorizer...")
        tfidf_matrix = self.vectorizer.fit_transform(texts)
        print("Fitting TruncatedSVD (384 dimensions) projection...")
        embeddings = self.svd.fit_transform(tfidf_matrix)
        
        # L2 normalize embeddings for dot-product cosine similarity
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return (embeddings / norms).astype(np.float32)

    def transform(self, texts: list[str]) -> np.ndarray:
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
        return embedder
