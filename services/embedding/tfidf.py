"""
Embedding / text-scoring layer (no app data).

Input: a query string and a corpus of text strings (any list of documents).
Output: the same texts with relevance scores (text, score, optional metadata),
in order of relevance. No IDs or mock data — pure "score these texts against
this query." Your teammate implements how (e.g. TF-IDF, embeddings).
"""

from dataclasses import dataclass
from typing import Iterable, List, Sequence


@dataclass
class ScoredText:
    text: str
    score: float
    metadata: dict | None = None


class TFIDFEmbedder:
    def __init__(self) -> None:
        pass

    def fit(self, corpus: Sequence[str]) -> None:
        raise NotImplementedError("Your teammate should implement this")

    def rank(
        self,
        query: str,
        corpus: Sequence[str],
        top_k: int | None = None,
    ) -> List[ScoredText]:
        raise NotImplementedError("Your teammate should implement this")


def rank_texts(
    query: str,
    texts: Iterable[str],
    top_k: int | None = None,
) -> List[ScoredText]:
    raise NotImplementedError("Your teammate should implement this")
