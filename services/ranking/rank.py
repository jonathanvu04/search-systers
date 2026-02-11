"""
Ranking layer for app responses (uses mock data).

Input: the mock response list (MOCK_RESPONSES) and a query string (the prompt).
Output: those responses ranked by relevance, in a form storable in the database —
each item must include text, score, and response_id (or equivalent) so we know
which response each row refers to. Your teammate may use the embedding layer
or implement ranking here; either way, output is DB-ready ranked responses.
"""

from dataclasses import dataclass
from typing import List

from services.embedding.tfidf import ScoredText


MOCK_PROMPT_TEXT = "What gets you up in the morning?"


@dataclass
class MockResponse:
    id: int
    text: str


MOCK_RESPONSES: List[MockResponse] = [
    MockResponse(
        id=1,
        text="Knowing that I get to make progress toward my long‑term goals.",
    ),
    MockResponse(
        id=2,
        text="My morning run and the quiet time I get before everyone else wakes up.",
    ),
    MockResponse(
        id=3,
        text="Coffee, sunlight, and the chance to show up better than I did yesterday.",
    ),
    MockResponse(
        id=4,
        text="Messages from friends in our group chat that always make me laugh.",
    ),
]


def get_ranked_mock_responses(
    query: str = MOCK_PROMPT_TEXT,
    top_k: int = 4,
) -> List[ScoredText]:
    raise NotImplementedError("Your teammate should implement this")
