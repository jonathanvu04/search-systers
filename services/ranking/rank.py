from typing import List, tuple
from __future__ import annotations
import numpy as np

def get_top_k_similar(
    current_embedding: list[float],
    current_response_id: int,
    others: list[tuple[int, list[float]]],
    top_k: int,
) -> list[tuple[int, float]]:
    """
    Input: current response embedding, its id, list of (response_id, embedding).
    Output: top-k (response_id, score) ordered by similarity (exclude current).
    Your teammate implements cosine similarity or equivalent.
    """
    raise NotImplementedError("Your teammate should implement this")


def cosine(query_vector: np.ndarray, candidate_vector: np.ndarray) -> float:
    #returns the cosine similarity between two 1D vectors. 1d
    '''
    if return 0.0 means no magnitude and the embedding prob off 
    - empty text
    - embedding failed, etc
    
    similarity = (query · candidate) / (||query|| * ||candidate||)
    '''
    
    query_norm = np.linalg.norm(query_vector) # Vector mags - Euclidean Norm
    candidate_norm = np.linalg.norm(candidate_vector)

    
    if query_norm == 0.0 or candidate_norm == 0.0:
        return 0.0

    # https://www.geeksforgeeks.org/python/how-to-calculate-cosine-similarity-in-python/
    return float(
        np.dot(query_vector, candidate_vector) / (query_norm * candidate_norm)
    )
    
    