"""Vector store helpers: compute embeddings, build/query FAISS index, and persist metadata.

Usage:
    from vector_store import (
        create_vector_store, load_vector_store, query_vector_store, build_embeddings
    )

    # Create and save index
    create_vector_store(texts, metadatas, index_path='data/processed/vector_store/index.faiss',
                        meta_path='data/processed/vector_store/metadata.pkl')

    # Load and query
    index, metas, model = load_vector_store('data/processed/vector_store/index.faiss',
                                           'data/processed/vector_store/metadata.pkl')
    results = query_vector_store(index, metas, 'example query', model, top_k=5)
"""
from __future__ import annotations

import os
import pickle
from typing import List, Tuple, Optional

import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except Exception as e:
    raise ImportError("Please install sentence-transformers to use vector_store (pip install sentence-transformers)")

try:
    import faiss
except Exception:
    raise ImportError("Please install faiss-cpu to use the FAISS index (pip install faiss-cpu)")


def build_embeddings(texts: List[str], model_name: str = "all-MiniLM-L6-v2", batch_size: int = 64) -> np.ndarray:
    """Compute embeddings for a list of texts using SentenceTransformers.

    Returns an array of shape (n_texts, dim).
    """
    model = SentenceTransformer(model_name)
    embeddings = model.encode(texts, batch_size=batch_size, show_progress_bar=True, convert_to_numpy=True)
    return embeddings


def build_faiss_index(embeddings: np.ndarray, normalize: bool = True) -> faiss.Index:
    """Create a FAISS IndexFlatIP index. If normalize is True, embeddings are L2-normalized and inner-product
    search acts as cosine similarity.
    """
    if normalize:
        # normalize in-place
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        embeddings = embeddings / norms

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    # Ensure contiguous array of type float32 and pass as keyword to satisfy type checkers
    emb32 = np.ascontiguousarray(embeddings.astype(np.float32))
    index.add(x=emb32)  # type: ignore
    return index


def save_faiss_index(index: faiss.Index, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    faiss.write_index(index, path)


def load_faiss_index(path: str) -> faiss.Index:
    if not os.path.exists(path):
        raise FileNotFoundError(f"FAISS index not found: {path}")
    return faiss.read_index(path)


def save_metadata(metadata: List[dict], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(metadata, f)


def load_metadata(path: str) -> List[dict]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Metadata file not found: {path}")
    with open(path, "rb") as f:
        return pickle.load(f)


def create_vector_store(texts: List[str], metadatas: List[dict], *,
                        index_path: str = "data/processed/vector_store/index.faiss",
                        meta_path: str = "data/processed/vector_store/metadata.pkl",
                        model_name: str = "all-MiniLM-L6-v2") -> Tuple[faiss.Index, List[dict], SentenceTransformer]:
    """Compute embeddings, build FAISS index, and persist both index and metadata.

    Returns (index, metadatas, model) for immediate querying.
    """
    if len(texts) != len(metadatas):
        raise ValueError("texts and metadatas must have the same length")

    print(f"Computing embeddings for {len(texts)} texts using {model_name}...")
    model = SentenceTransformer(model_name)
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

    print("Building FAISS index...")
    # Normalize for cosine similarity
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    embeddings = embeddings / norms
    index = build_faiss_index(embeddings, normalize=False)

    print(f"Saving index to {index_path} and metadata to {meta_path}...")
    save_faiss_index(index, index_path)
    save_metadata(metadatas, meta_path)

    return index, metadatas, model


def load_vector_store(index_path: str = "data/processed/vector_store/index.faiss",
                      meta_path: str = "data/processed/vector_store/metadata.pkl",
                      model_name: str = "all-MiniLM-L6-v2") -> Tuple[faiss.Index, List[dict], SentenceTransformer]:
    """Load FAISS index and metadata; also return a SentenceTransformer instance for queries.
    """
    index = load_faiss_index(index_path)
    metas = load_metadata(meta_path)
    model = SentenceTransformer(model_name)
    return index, metas, model


def query_vector_store(index: faiss.Index, metadatas: List[dict], query: str, model: SentenceTransformer,
                       top_k: int = 5) -> List[Tuple[float, dict]]:
    """Query the index with a string and return list of (score, metadata) tuples.

    Scores are cosine similarity in [0,1] when the stored index uses normalized embeddings.
    """
    q_emb = model.encode([query], convert_to_numpy=True)
    q_emb = np.ascontiguousarray(q_emb.astype(np.float32))
    # normalize
    q_emb = q_emb / (np.linalg.norm(q_emb, axis=1, keepdims=True) + 1e-12)

    # Use keyword args to match FAISS Python signatures in type stubs
    D, I = index.search(x=q_emb, k=top_k)  # type: ignore
    results = []
    for score, idx in zip(D[0], I[0]):
        if idx < 0 or idx >= len(metadatas):
            continue
        results.append((float(score), metadatas[int(idx)]))
    return results
