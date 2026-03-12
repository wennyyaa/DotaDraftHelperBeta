from ..data.hero_attributes import (
    ANTI_ILLUSION_HEROES,
    BURST_OR_LOCKDOWN_HEROES,
    DISABLE_HEROES,
    EARLY_TEMPO_HEROES,
    FLEX_SAFE_HEROES,
    FRONTLINE_HEROES,
    HERO_ROLES,
    HERO_SCALING,
    ILLUSION_OR_SUMMON_HEROES,
    LANE_COUNTER_RULES,
    PUSH_HEROES,
    SAVE_HEROES,
    SPECIAL_THREAT_RULES,
)


def lane_matchup_score(hero: str, enemies: list[str], allies: list[str]) -> tuple[float, list[str]]:
    score = 0.0
    reasons: list[str] = []

    hero_lane_rules = LANE_COUNTER_RULES.get(hero, {})
    for enemy in enemies:
        bonus = hero_lane_rules.get(enemy)
        if bonus:
            score += bonus
            reasons.append(f"Strong lane matchup vs {enemy}")

    for enemy in enemies:
        counters_for_enemy = SPECIAL_THREAT_RULES.get(enemy, {})
        bonus = counters_for_enemy.get(hero)
        if bonus:
            score += bonus
            reasons.append(f"Special answer to {enemy}")

    return round(score, 1), reasons

def get_draft_phase(allies: list[str], enemies: list[str]) -> str:
    total_picked = len(allies) + len(enemies)

    if total_picked <= 3:
        return "early"

    if total_picked <= 6:
        return "mid"

    return "late"


def draft_phase_score(hero: str, allies: list[str], enemies: list[str]) -> tuple[float, list[str]]:
    phase = get_draft_phase(allies, enemies)

    if phase == "early":
        if hero in FLEX_SAFE_HEROES:
            return 0.8, ["Safe and flexible early pick"]
        return 0.0, []

    if phase == "mid":
        if hero in FLEX_SAFE_HEROES:
            return 0.3, ["Stable mid-draft option"]
        return 0.0, []

    return 0.0, []


def save_score(hero: str, allies: list[str], enemies: list[str]) -> tuple[float, list[str]]:
    if hero not in SAVE_HEROES:
        return 0.0, []

    ally_save_count = sum(1 for ally in allies if ally in SAVE_HEROES)
    enemy_threat_count = sum(1 for enemy in enemies if enemy in BURST_OR_LOCKDOWN_HEROES)

    if enemy_threat_count == 0:
        return 0.0, []

    if ally_save_count == 0 and enemy_threat_count >= 1:
        return 1.0, ["Provides defensive save"]

    if ally_save_count == 1 and enemy_threat_count >= 2:
        return 0.5, ["Adds extra protection for allies"]

    return 0.0, []


def anti_illusion_score(hero: str, enemies: list[str]) -> tuple[float, list[str]]:
    illusion_enemy = any(enemy in ILLUSION_OR_SUMMON_HEROES for enemy in enemies)

    if not illusion_enemy:
        return 0.0, []

    if hero in ANTI_ILLUSION_HEROES:
        return 1.2, ["Strong against illusions and summons"]

    return 0.0, []


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

    anti_score, anti_reasons = anti_illusion_score(hero, enemies)
    total_score += anti_score
    all_reasons.extend(anti_reasons)

    save_bonus, save_reasons = save_score(hero, allies, enemies)
    total_score += save_bonus
    all_reasons.extend(save_reasons)

    phase_bonus, phase_reasons = draft_phase_score(hero, allies, enemies)
    total_score += phase_bonus
    all_reasons.extend(phase_reasons)

    lane_bonus, lane_reasons = lane_matchup_score(hero, enemies, allies)
    total_score += lane_bonus
    all_reasons.extend(lane_reasons)

    return round(total_score, 1), all_reasons