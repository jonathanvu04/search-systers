"""
TF-IDF embedding: take a response, vectorize it, L2-normalize for DB storage.
Called fresh for every new response 
"""

from typing import List

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


def embed_all(corpus: List[str]) -> List[List[float]]:
    """
    Fit TF-IDF on corpus, transform all texts, L2-normalize each.
    Use when adding a new response: recompute embeddings for ALL responses
    so vocabulary and IDF stay consistent.

    Returns:
        List of L2-normalized vectors (one per document).
    """
    if not corpus:
        return []

    vectorizer = TfidfVectorizer(
        sublinear_tf=True,
        lowercase=True,
        stop_words="english",
        max_features=1000,
    )
    vectors = vectorizer.fit_transform(corpus)

    result: List[List[float]] = []
    for i in range(vectors.shape[0]):
        vec = vectors[i].toarray().flatten().astype(np.float64)
        norm = np.linalg.norm(vec)
        if norm == 0:
            result.append([0.0] * len(vec))
        else:
            result.append((vec / norm).tolist())
    return result


def embed(text: str, corpus: List[str]) -> List[float]:
    """
    Steps 3–4: Fit TF-IDF on corpus, transform text, L2-normalize.

    Args:
        text: The new response to embed.
        corpus: All response texts for this prompt_id (including text).
                Establishes shared vocabulary and IDF.

    Returns:
        L2-normalized vector as list of floats for DB storage.
        Normalized vectors: cosine_sim(a, b) = dot(a, b).
    """
    if not corpus:
        corpus = [text]
    elif text not in corpus:
        corpus = list(corpus) + [text]

    vectorizer = TfidfVectorizer(
        sublinear_tf=True,
        lowercase=True,
        stop_words="english",
        max_features=1000,
    )
    vectors = vectorizer.fit_transform(corpus)

    idx = len(corpus) - 1 if corpus[-1] == text else corpus.index(text)
    vec = vectors[idx].toarray().flatten().astype(np.float64)

    norm = np.linalg.norm(vec)
    if norm == 0:
        return [0.0] * len(vec)

    return (vec / norm).tolist()
