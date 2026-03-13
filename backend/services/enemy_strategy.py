# backend/services/enemy_strategy.py

from typing import List, Tuple

ILLUSION_HEROES = {
    "Phantom Lancer",
    "Naga Siren",
    "Chaos Knight",
    "Terrorblade",
}

ZOO_HEROES = {
    "Beastmaster",
    "Chen",
    "Enchantress",
    "Nature's Prophet",
    "Lycan",
}

MOBILE_HEROES = {
    "Storm Spirit",
    "Ember Spirit",
    "Puck",
    "Queen of Pain",
    "Void Spirit",
}

SUSTAIN_HEROES = {
    "Necrophos",
    "Abaddon",
    "Dazzle",
    "Omniknight",
}


def detect_enemy_strategy(enemies: List[str]) -> List[str]:
    strategies: List[str] = []

    illusion_count = sum(hero in ILLUSION_HEROES for hero in enemies)
    zoo_count = sum(hero in ZOO_HEROES for hero in enemies)
    mobile_count = sum(hero in MOBILE_HEROES for hero in enemies)
    sustain_count = sum(hero in SUSTAIN_HEROES for hero in enemies)

    if illusion_count >= 2:
        strategies.append("illusion")

    if zoo_count >= 2:
        strategies.append("zoo")

    if mobile_count >= 2:
        strategies.append("mobile")

    if sustain_count >= 2:
        strategies.append("sustain")

    return strategies


def strategy_counter_score(hero: str, strategies: List[str]) -> Tuple[float, List[str]]:
    score = 0.0
    reasons: List[str] = []

    # illusion counters
    if "illusion" in strategies:
        if hero in {"Earthshaker", "Sven", "Axe", "Leshrac", "Underlord"}:
            score += 1.5
            reasons.append("Strong against illusion draft")

    # zoo counters
    if "zoo" in strategies:
        if hero in {"Earthshaker", "Dark Seer", "Underlord", "Sand King"}:
            score += 1.2
            reasons.append("Good vs zoo / summon strategy")

    # mobile heroes counters
    if "mobile" in strategies:
        if hero in {"Lion", "Shadow Shaman", "Centaur Warrunner", "Axe"}:
            score += 1.0
            reasons.append("Adds control vs mobile cores")

    # sustain counters
    if "sustain" in strategies:
        if hero in {"Ancient Apparition"}:
            score += 2.0
            reasons.append("Shuts down sustain healing")

    return round(score, 1), reasons