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
    "Viper": {"Huskar": 3.0, "Timbersaw": 2.0, "Bristleback": 1.8, "Dragon Knight": 1.2},
    "Necrophos": {"Huskar": 3.0, "Axe": 1.5, "Centaur Warrunner": 1.0, "Bristleback": 1.0},
    "Ancient Apparition": {"Huskar": 2.2, "Alchemist": 1.5, "Morphling": 1.2, "Necrophos": 1.0},

    # Illusions / summons
    "Earthshaker": {"Naga Siren": 3.0, "Phantom Lancer": 3.0, "Chaos Knight": 2.0},
    "Sven": {"Terrorblade": 2.5, "Phantom Lancer": 2.0, "Naga Siren": 1.8, "Chaos Knight": 1.5},
    "Leshrac": {"Phantom Lancer": 2.5, "Naga Siren": 2.2, "Broodmother": 1.5},
    "Underlord": {"Phantom Lancer": 2.0, "Naga Siren": 1.8, "Broodmother": 1.4},
    "Axe": {"Phantom Lancer": 2.2, "Naga Siren": 1.6, "Chaos Knight": 1.4},

    # Spirits / mobile heroes
    "Silencer": {"Storm Spirit": 2.5, "Ember Spirit": 1.4, "Void Spirit": 1.4, "Puck": 1.2},
    "Lion": {"Storm Spirit": 1.8, "Ember Spirit": 1.0, "Anti-Mage": 1.0, "Morphling": 1.0},
    "Shadow Shaman": {"Storm Spirit": 1.6, "Ember Spirit": 0.8, "Puck": 0.8},
    "Spirit Breaker": {"Storm Spirit": 1.8, "Tinker": 1.5, "Sniper": 1.0},

    # Specific cores
    "Anti-Mage": {"Medusa": 2.5, "Storm Spirit": 1.2, "Zeus": 1.0},
    "Nyx Assassin": {"Medusa": 1.6, "Tinker": 1.8, "Leshrac": 1.0, "Pugna": 1.0},
    "Oracle": {"Legion Commander": 1.3, "Batrider": 1.0, "Doom": 1.0},
    "Dazzle": {"Legion Commander": 1.2, "Axe": 0.8},
    "Abaddon": {"Legion Commander": 1.0, "Bane": 0.8},
}

# Synergy rules between heroes on the same team.
SYNERGIES: Dict[str, Dict[str, float]] = {
    # Arena combos
    "Phoenix": {"Mars": 2.0},
    "Snapfire": {"Mars": 2.0, "Faceless Void": 1.8},
    "Dark Willow": {"Mars": 1.2},
    "Puck": {"Mars": 1.5, "Faceless Void": 1.5},

    # Magnus empower / melee cores
    "Phantom Assassin": {"Magnus": 2.0},
    "Juggernaut": {"Magnus": 1.2},
    "Ursa": {"Magnus": 1.2},
    "Sven": {"Magnus": 1.0, "Dazzle": 1.5, "Oracle": 1.5},

    # Save / buff style synergies
    "Huskar": {"Oracle": 2.5, "Dazzle": 1.8},
    "Drow Ranger": {"Vengeful Spirit": 1.4, "Treant Protector": 1.0},
    "Terrorblade": {"Shadow Demon": 2.0, "Dazzle": 1.2},

    # Wombo / teamfight
    "Invoker": {"Faceless Void": 2.0},
    "Witch Doctor": {"Faceless Void": 1.6, "Magnus": 1.2},
    "Jakiro": {"Faceless Void": 1.4, "Mars": 1.0},
    "Enigma": {"Phoenix": 1.2, "Jakiro": 1.0},

    # Ion shell / melee jumpers
    "Dark Seer": {"Spirit Breaker": 1.8, "Sven": 1.2, "Ursa": 1.0, "Night Stalker": 1.0},

    # Push / zoo / objective taking
    "Shadow Shaman": {"Death Prophet": 1.2, "Leshrac": 1.2, "Beastmaster": 1.0},
    "Nature's Prophet": {"Beastmaster": 1.0, "Chen": 1.0},
}

# Weak matchups where a hero is punished by specific enemies.
WEAKNESSES: Dict[str, Dict[str, float]] = {
    # Existing
    "Templar Assassin": {"Viper": 3.0, "Venomancer": 2.0},

    # Mobility punished
    "Storm Spirit": {"Silencer": 2.5, "Lion": 1.8, "Shadow Shaman": 1.5, "Spirit Breaker": 1.2},
    "Ember Spirit": {"Silencer": 1.8, "Lion": 1.2, "Shadow Shaman": 1.0},
    "Puck": {"Silencer": 1.8, "Dragon Knight": 0.8},
    "Morphling": {"Ancient Apparition": 2.0, "Lion": 1.0, "Nyx Assassin": 0.8},

    # Illusion heroes into AoE
    "Phantom Lancer": {"Earthshaker": 3.0, "Sven": 2.2, "Leshrac": 2.0, "Underlord": 1.6, "Axe": 1.6},
    "Naga Siren": {"Earthshaker": 3.0, "Sven": 2.0, "Leshrac": 2.0, "Underlord": 1.5},
    "Chaos Knight": {"Earthshaker": 2.0, "Sven": 1.6, "Axe": 1.0},
    "Terrorblade": {"Sven": 2.5, "Leshrac": 1.5},

    # Regen / sustain cores
    "Huskar": {"Viper": 3.0, "Necrophos": 2.5, "Ancient Apparition": 2.0},
    "Timbersaw": {"Viper": 2.0, "Outworld Devourer": 1.2},
    "Medusa": {"Anti-Mage": 2.5, "Nyx Assassin": 1.5},

    # Vulnerable push/summon styles
    "Broodmother": {"Leshrac": 1.8, "Underlord": 1.5, "Axe": 1.2},
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

