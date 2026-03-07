from __future__ import annotations
from typing import List, Tuple, Optional
import numpy as np


def cosine(query_vector: np.ndarray, candidate_vector: np.ndarray) -> float:
    #returns the cosine similarity between two 1D vectors. 1d
    '''
    if return 0.0 means no magnitude and the embedding prob off 
    - empty text
    - embedding failed, etc
    
    similarity = (query · candidate) / (||query|| * ||candidate||)
    '''
    query_norm = np.linalg.norm(query_vector)
    candidate_norm = np.linalg.norm(candidate_vector)

    if query_norm == 0.0 or candidate_norm == 0.0:
        return 0.0

    return float(np.dot(query_vector, candidate_vector) / (query_norm * candidate_norm))


