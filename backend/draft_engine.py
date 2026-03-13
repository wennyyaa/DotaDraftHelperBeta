"""Backwards-compatible wrapper around the draft recommendation engine.

The real implementation now lives in `backend.engines.rule_engine` and is
typically accessed via `backend.services.draft_service`. This module remains
only to avoid breaking any older imports.
"""

from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

from .services import draft_service

def classify_confidence(score: float) -> str:
    if score >= 5.0:
        return "best-pick"

    if score >= 3.0:
        return "strong-fit"

    if score >= 1.5:
        return "situational"

    return "risky"

def recommend_with_explanations(
    allies: Sequence[str],
    enemies: Sequence[str],
    k: int = 5,
) -> Tuple[List[str], Dict[str, Dict[str, object]]]:
    return draft_service.get_recommendations_with_explanations(allies, enemies, k=k)


def recommend_heroes(
    allies: Sequence[str],
    enemies: Sequence[str],
    k: int = 5,
) -> List[str]:
    heroes, _ = recommend_with_explanations(allies, enemies, k=k)
    return heroes


def get_recommendations(allies: Sequence[str], enemies: Sequence[str]) -> List[str]:
    return draft_service.get_recommendations(allies, enemies, k=5)

