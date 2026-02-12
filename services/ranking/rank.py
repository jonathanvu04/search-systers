from typing import List


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
