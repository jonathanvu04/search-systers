"""
Semantic embedding via sentence-transformers (all-MiniLM-L6-v2).
384-dim, L2-normalized. Embed each text independently (no corpus dependency).
"""

from typing import List

_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _model


def embed(text: str) -> List[float]:
    """
    Embed a single text. Returns L2-normalized 384-dim vector.
    Cosine similarity = dot product for normalized vectors.
    """
    model = _get_model()
    vec = model.encode(text, normalize_embeddings=True)
    return vec.tolist()


def embed_batch(texts: List[str]) -> List[List[float]]:
    """
    Embed multiple texts. For backfill. Returns list of L2-normalized vectors.
    """
    if not texts:
        return []
    model = _get_model()
    vecs = model.encode(texts, normalize_embeddings=True)
    return [v.tolist() for v in vecs]
