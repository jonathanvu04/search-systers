from __future__ import annotations
from typing import List, Tuple
import numpy as np


def cosine(query_vector: np.ndarray, candidate_vector: np.ndarray) -> float:
    """
    Compute cosine similarity between two 1D vectors.

    Returns 0.0 if either vector has zero magnitude.
    """
    query_norm = np.linalg.norm(query_vector)
    candidate_norm = np.linalg.norm(candidate_vector)

    if query_norm == 0.0 or candidate_norm == 0.0:
        return 0.0

    return float(np.dot(query_vector, candidate_vector) / (query_norm * candidate_norm))


def get_top_k_similar(
    current_embedding: list[float],
    current_response_id: int,
    others: list[tuple[int, list[float]]],
    top_k: int,
    min_score: float = 0.0,
) -> list[tuple[int, float]]:
    """
    Rank candidate responses by cosine similarity.

    Inputs:
    - current_embedding: embedding of the current/query response
    - current_response_id: ID of the query response
    - others: list of (response_id, embedding) candidate responses
    - top_k: number of results to return
    - min_score: optional minimum similarity threshold

    Returns:
    - list of (response_id, similarity_score), sorted descending
    """

    if top_k <= 0:
        return []

    query_vector = np.asarray(current_embedding, dtype=np.float32)
    if query_vector.ndim != 1 or query_vector.size == 0:
        return []

    expected_dim = query_vector.shape[0]
    scored: List[Tuple[int, float]] = []

    for response_id, embedding in others:
        # Exclude the current response itself
        if response_id == current_response_id:
            continue

        candidate_vector = np.asarray(embedding, dtype=np.float32)

        # Skip malformed candidate embeddings
        if candidate_vector.ndim != 1:
            continue
        if candidate_vector.size == 0:
            continue
        if candidate_vector.shape[0] != expected_dim:
            continue

        similarity_score = cosine(query_vector, candidate_vector)

        # Keep only candidates above the minimum relevance threshold
        if similarity_score >= min_score:
            scored.append((response_id, similarity_score))


    scored.sort(key=lambda x: x[1], reverse=True)

    return scored[:top_k]