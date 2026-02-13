from typing import List, Tuple
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
    
    This function:
    1. Receives a query embedding (the user's response)
    2. Compares it to candidate embeddings
    3. Computes cosine similarity for each
    4. Returns the top-k most similar responses
    
    returns: 
    List of tuples:
        [(response_id, similarity_score), ...]
        Sorted in descending order by similarity.
    """
    # Convert query embedding to NumPy array once for efficiency
    q = np.asarray(current_embedding, dtype=np.float32)

    # In the format (response_id, similarity_score)
    scored: List[Tuple[int, float]] = []


    for resp_id, emb in others:
        # exclude itself
        if resp_id == current_response_id:
            continue

        # Convert candidate embedding to NumPy array
        v = np.asarray(emb, dtype=np.float32)

        similarity = cosine(q, v)
        scored.append((resp_id, similarity))

    # Sort by similarity score in descending order
    scored.sort(key=lambda x: x[1], reverse=True)

    return scored[:top_k]
   # raise NotImplementedError("Your teammate should implement this")


def cosine(query_vector: np.ndarray, candidate_vector: np.ndarray) -> float:
    #returns the cosine similarity between two 1D vectors. 1d
    '''
    if return 0.0 means no magnitude and the embedding prob off 
    - empty text
    - embedding failed, etc
    
    similarity = (query dot candidate) / (||query|| * ||candidate||)
    '''
    
    query_norm = np.linalg.norm(query_vector) # Vector mags - Euclidean Norm
    candidate_norm = np.linalg.norm(candidate_vector)

    
    if query_norm == 0.0 or candidate_norm == 0.0:
        return 0.0

    # https://www.geeksforgeeks.org/python/how-to-calculate-cosine-similarity-in-python/
    return float(
        np.dot(query_vector, candidate_vector) / (query_norm * candidate_norm)
    )
    
    