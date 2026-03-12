from ..data.hero_attributes import (
    DISABLE_HEROES,
    EARLY_TEMPO_HEROES,
    FRONTLINE_HEROES,
    HERO_ROLES,
    HERO_SCALING,
    PUSH_HEROES,
)


def role_balance_score(hero: str, allies: list[str]) -> tuple[float, list[str]]:
    ally_roles = []
    for ally in allies:
        ally_roles.extend(HERO_ROLES.get(ally, []))

    hero_roles = HERO_ROLES.get(hero, [])

    score = 0.0
    reasons = []

    if "support" not in ally_roles and "support" in hero_roles:
        score += 1.2
        reasons.append("Fills missing support role")

    if "carry" not in ally_roles and "carry" in hero_roles:
        score += 1.0
        reasons.append("Fills missing carry role")

    if "offlane" not in ally_roles and "offlane" in hero_roles:
        score += 0.8
        reasons.append("Adds offlane presence")

    return score, reasons


def frontline_score(hero: str, allies: list[str]) -> tuple[float, list[str]]:
    ally_frontliners = sum(1 for ally in allies if ally in FRONTLINE_HEROES)

    if hero not in FRONTLINE_HEROES:
        return 0.0, []

    if ally_frontliners == 0:
        return 1.2, ["Adds frontline durability"]

    if ally_frontliners == 1:
        return 0.5, ["Improves team durability"]

    return 0.0, []


def scaling_score(hero: str, allies: list[str]) -> tuple[float, list[str]]:
    ally_scaling = sum(1 for ally in allies if HERO_SCALING.get(ally) == "late")

    if HERO_SCALING.get(hero) != "late":
        return 0.0, []

    if ally_scaling == 0:
        return 0.8, ["Adds strong late-game scaling"]

    if ally_scaling == 1:
        return 0.3, ["Improves late-game potential"]

    return 0.0, []


def disable_score(hero: str, allies: list[str]) -> tuple[float, list[str]]:
    ally_disable = sum(1 for ally in allies if ally in DISABLE_HEROES)

    if hero not in DISABLE_HEROES:
        return 0.0, []

    if ally_disable == 0:
        return 1.0, ["Adds reliable control"]

    if ally_disable == 1:
        return 0.4, ["Improves team lockdown"]

    return 0.0, []


def push_score(hero: str, allies: list[str]) -> tuple[float, list[str]]:
    ally_push = sum(1 for ally in allies if ally in PUSH_HEROES)

    if hero not in PUSH_HEROES:
        return 0.0, []

    if ally_push == 0:
        return 0.6, ["Adds tower pressure"]

    return 0.0, []


def tempo_score(hero: str, allies: list[str]) -> tuple[float, list[str]]:
    ally_tempo = sum(1 for ally in allies if ally in EARLY_TEMPO_HEROES)

    if hero not in EARLY_TEMPO_HEROES:
        return 0.0, []

    if ally_tempo == 0:
        return 0.7, ["Adds early tempo"]

    if ally_tempo == 1:
        return 0.3, ["Improves early game pressure"]

    return 0.0, []


def team_needs_score(hero: str, allies: list[str], enemies: list[str]) -> tuple[float, list[str]]:
    total_score = 0.0
    all_reasons: list[str] = []

    scorers = [
        role_balance_score,
        frontline_score,
        scaling_score,
        disable_score,
        push_score,
        tempo_score,
    ]

    for scorer in scorers:
        score, reasons = scorer(hero, allies)
        total_score += score
        all_reasons.extend(reasons)

    return round(total_score, 1), all_reasons