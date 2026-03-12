from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from ..heroes import HERO_POOL  # shared hero pool; engine can be replaced by ml_engine later

@dataclass(frozen=True)
class RuleScores:
  """Container for rule-based scores applied to a single hero."""

  score: float
  reasons: List[str]


# Simple handcrafted matchup rules.
COUNTERS: Dict[str, Dict[str, float]] = {
    # Lane/HP burning cores
    "Viper": {"Huskar": 3.0, "Timbersaw": 2.0},
    "Necrophos": {"Huskar": 3.0, "Axe": 1.5},
    # Illusion clear / armor shred
    "Earthshaker": {"Naga Siren": 3.0, "Phantom Lancer": 3.0},
    "Sven": {"Terrorblade": 2.5},
}

# Synergy rules between heroes on the same team.
SYNERGIES: Dict[str, Dict[str, float]] = {
    # Arena + save / sustain
    "Dazzle": {"Mars": 2.0},
    # Dream Coil + Arena style teamfight
    "Puck": {"Mars": 1.5, "Faceless Void": 1.5},
    # Buffed right-clickers
    "Sven": {"Dazzle": 1.5, "Oracle": 1.5},
}

# Weak matchups where a hero is punished by specific enemies.
WEAKNESSES: Dict[str, Dict[str, float]] = {
    # Armor reduction / damage over time vs refraction
    "Templar Assassin": {"Viper": 3.0, "Venomancer": 2.0},
}


def _norm(names: Iterable[str]) -> List[str]:
    """Normalize hero name input (strip whitespace, drop empties)."""

    return [n.strip() for n in names if n and n.strip()]


def _apply_rule_table(
    table: Mapping[str, Mapping[str, float]],
    hero: str,
    others: Sequence[str],
    label: str,
) -> RuleScores:
    """Apply a single rule table (counters, synergies, weaknesses)."""

    total = 0.0
    reasons: List[str] = []

    rules_for_hero = table.get(hero, {})
    for other in others:
        if other not in rules_for_hero:
            continue

        delta = rules_for_hero[other]
        if label == "weakness":
            total -= delta
            reasons.append(f"-{delta} vs {other} ({label})")
        else:
            total += delta
            reasons.append(f"+{delta} vs {other} ({label})")

    return RuleScores(score=total, reasons=reasons)


def score_hero(
    hero: str,
    allies: Sequence[str],
    enemies: Sequence[str],
) -> Tuple[float, List[str]]:
    """Score a single hero using simple handcrafted rules."""

    counters_score = _apply_rule_table(COUNTERS, hero, enemies, label="counter")
    synergy_score = _apply_rule_table(SYNERGIES, hero, allies, label="synergy")
    weakness_score = _apply_rule_table(WEAKNESSES, hero, enemies, label="weakness")

    total = counters_score.score + synergy_score.score + weakness_score.score
    reasons: List[str] = (
        counters_score.reasons + synergy_score.reasons + weakness_score.reasons
    )

    return total, reasons


def recommend_heroes(
    allies: Sequence[str],
    enemies: Sequence[str],
    k: int = 5,
) -> List[str]:
    """Return the top-k hero names using only rule-based scores."""

    allies_n = _norm(allies)
    enemies_n = _norm(enemies)

    taken = set(allies_n) | set(enemies_n)

    scored: List[Tuple[str, float]] = []
    for hero in HERO_POOL:
        if hero in taken:
            continue
        score, _ = score_hero(hero, allies=allies_n, enemies=enemies_n)
        scored.append((hero, score))

    scored.sort(key=lambda x: (-x[1], x[0]))
    return [h for h, _ in scored[: max(0, int(k))]]


def recommend_with_explanations(
    allies: Sequence[str],
    enemies: Sequence[str],
    k: int = 5,
) -> Tuple[List[str], Dict[str, Dict[str, object]]]:
    """Return top-k heroes plus detailed rule-based explanations."""

    allies_n = _norm(allies)
    enemies_n = _norm(enemies)
    taken = set(allies_n) | set(enemies_n)

    details: Dict[str, Dict[str, object]] = {}
    scored: List[Tuple[str, float]] = []

    for hero in HERO_POOL:
        if hero in taken:
            continue
        score, reasons = score_hero(hero, allies=allies_n, enemies=enemies_n)
        details[hero] = {"score": score, "reasons": reasons}
        scored.append((hero, score))

    scored.sort(key=lambda x: (-x[1], x[0]))
    top_heroes = [h for h, _ in scored[: max(0, int(k))]]

    explanations = {h: details[h] for h in top_heroes}
    return top_heroes, explanations

