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
from .archetype_engine import archetype_score
from .enemy_strategy import detect_enemy_strategy, strategy_counter_score
from .features_engines import get_hero_features, team_feature_summary
from .slot_features import slot_missing_roles


def ally_slot_score(hero: str, ally_slots=None) -> tuple[float, list[str]]:
    

    if not ally_slots:
        return 0.0, []

    hero_roles = HERO_ROLES.get(hero, [])
    missing_roles = slot_missing_roles(ally_slots)

    score = 0.0
    reasons: list[str] = []

    for role in missing_roles:
        if role in hero_roles:
            if role == "carry":
                score += 1.8
            elif role == "mid":
                score += 1.3
            elif role == "offlane":
                score += 1.6
            elif role == "support":
                score += 1.4

            reasons.append(f"Fits open {role} slot")

    slot_data = ally_slots.model_dump()

    filled_roles = []
    if slot_data.get("carry"):
        filled_roles.append("carry")
    if slot_data.get("mid"):
        filled_roles.append("mid")
    if slot_data.get("offlane"):
        filled_roles.append("offlane")
    if slot_data.get("support") or slot_data.get("hard_support"):
        filled_roles.append("support")

    if filled_roles and not any(role in missing_roles for role in hero_roles):
        overlap_with_filled = [role for role in hero_roles if role in filled_roles]
        if overlap_with_filled:
            score -= 0.5
            reasons.append("Most natural role already filled")

    return round(score, 1), reasons


def add_bucket_score(
    buckets: dict[str, float],
    bucket_name: str,
    score: float,
    cap: float,
) -> float:

    current = buckets.get(bucket_name, 0.0)

    if score <= 0:
        buckets[bucket_name] = current + score
        return score

    remaining = cap - current
    if remaining <= 0:
        return 0.0

    applied = min(score, remaining)
    buckets[bucket_name] = current + applied
    return applied

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

    return round(score, 1), reasons


def infer_team_roles(allies: list[str]) -> dict[str, int]:
    role_counts = {
        "carry": 0,
        "mid": 0,
        "offlane": 0,
        "support": 0,
    }

    for ally in allies:
        for role in HERO_ROLES.get(ally, []):
            if role in role_counts:
                role_counts[role] += 1

    return role_counts


def role_inference_score(hero: str, allies: list[str]) -> tuple[float, list[str]]:
    role_counts = infer_team_roles(allies)
    hero_roles = HERO_ROLES.get(hero, [])

    score = 0.0
    reasons: list[str] = []

    for role, count in role_counts.items():
        if count == 0 and role in hero_roles:
            if role == "carry":
                score += 1.6
            elif role == "mid":
                score += 1.1
            elif role == "offlane":
                score += 1.4
            elif role == "support":
                score += 1.0
            reasons.append(f"Team lacks {role}")

    for role, count in role_counts.items():
        if count >= 2 and role in hero_roles:
            if role == "support":
                score -= 0.7
            else:
                score -= 0.5
            reasons.append(f"Too many {role}s already")

    return round(score, 1), reasons


def feature_reasoning_score(hero: str, allies: list[str]) -> tuple[float, list[str]]:
    team_summary = team_feature_summary(allies)
    hero_features = get_hero_features(hero)

    score = 0.0
    reasons: list[str] = []

    if team_summary["frontline"] == 0 and hero_features.get("frontline", 0) == 1:
        score += 1.0
        reasons.append("Provides needed frontline")

    if team_summary["control"] <= 1 and hero_features.get("control", 0) == 1:
        score += 0.8
        reasons.append("Adds reliable control")

    if team_summary["teamfight"] == 0 and hero_features.get("teamfight", 0) == 1:
        score += 0.7
        reasons.append("Improves teamfight presence")

    if team_summary["push"] == 0 and hero_features.get("push", 0) == 1:
        score += 0.6
        reasons.append("Adds objective pressure")

    if team_summary["save"] == 0 and hero_features.get("save", 0) == 1:
        score += 0.6
        reasons.append("Provides defensive utility")

    if team_summary["scaling"] == 0 and hero_features.get("scaling", 0) == 1:
        score += 0.6
        reasons.append("Improves late-game scaling")

    return round(score, 1), reasons


def archetype_reasoning_score(hero: str, allies: list[str]) -> tuple[float, list[str]]:
    hero_features = get_hero_features(hero)
    return archetype_score(hero, allies, hero_features)


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
        return 1.0, ["Adds strong late-game scaling"]

    if ally_scaling == 1:
        return 0.4, ["Improves late-game potential"]

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


def negative_reasoning_score(hero: str, allies: list[str]) -> tuple[float, list[str]]:
    score = 0.0
    reasons: list[str] = []

    hero_features = get_hero_features(hero)
    team_summary = team_feature_summary(allies)

    if hero_features.get("frontline", 0) == 1 and team_summary["frontline"] >= 2:
        score -= 0.5
        reasons.append("Team already has enough frontline")

    if hero_features.get("control", 0) == 1 and team_summary["control"] >= 3:
        score -= 0.4
        reasons.append("Draft already has strong control")

    if hero_features.get("scaling", 0) == 1 and team_summary["scaling"] >= 2:
        score -= 0.4
        reasons.append("Team may become too greedy")

    if hero_features.get("push", 0) == 1 and team_summary["push"] >= 2:
        score -= 0.3
        reasons.append("Push pressure already covered")

    return round(score, 1), reasons

def normalize_role(role: str | None) -> str | None:
    if role == "hard_support":
        return "support"
    return role

def role_preference_score(hero: str, target_role: str | None) -> tuple[float, list[str]]:
    target_role = normalize_role(target_role)

    if not target_role:
        return 0.0, []

    hero_roles = HERO_ROLES.get(hero, [])

    if target_role in hero_roles:
        return 2.5, [f"Preferred {target_role} pick for this draft"]

    return -0.3, []


def anti_illusion_score(hero: str, enemies: list[str]) -> tuple[float, list[str]]:
    illusion_enemy = any(enemy in ILLUSION_OR_SUMMON_HEROES for enemy in enemies)

    if not illusion_enemy:
        return 0.0, []

    if hero in ANTI_ILLUSION_HEROES:
        return 1.2, ["Strong against illusions and summons"]

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
def hard_counter_priority_score(
    hero: str,
    enemies: list[str],
    target_role: str | None = None,
) -> tuple[float, list[str]]:
    score = 0.0
    reasons: list[str] = []

    from ..engines.rule_engine import COUNTERS

    hero_roles = HERO_ROLES.get(hero, [])
    role_matches = not target_role or target_role in hero_roles

    hero_counter_map = COUNTERS.get(hero, {})

    if not hero_counter_map:
        return 0.0, []

    best_counter_strength = 0.0
    best_enemy = None

    for enemy in enemies:
        if enemy not in hero_counter_map:
            continue

        counter_strength = float(hero_counter_map[enemy])

        if counter_strength > best_counter_strength:
            best_counter_strength = counter_strength
            best_enemy = enemy

    if best_enemy is None:
        return 0.0, []

    # Keep counter influence noticeable, but not overwhelming.
    if role_matches:
        if best_counter_strength >= 3.0:
            score = 1.0
            reasons.append(f"Strong counter to {best_enemy}")
        elif best_counter_strength >= 2.0:
            score = 0.5
            reasons.append(f"Counters {best_enemy}")
    else:
        # Off-role counters should barely matter.
        if best_counter_strength >= 3.0:
            score = 0.15
        elif best_counter_strength >= 2.0:
            score = 0.05

    return round(score, 1), reasons


def enemy_strategy_score(
    hero: str,
    enemies: list[str],
    target_role: str | None = None,
) -> tuple[float, list[str]]:
    score = 0.0
    reasons = []

    hero_roles = HERO_ROLES.get(hero, [])

    illusion_heroes = {"Phantom Lancer", "Naga Siren", "Terrorblade"}
    heal_heroes = {"Huskar", "Alchemist", "Necrophos"}
    mobile_heroes = {"Storm Spirit", "Ember Spirit", "Puck", "Void Spirit"}

    hero_aoe = {"Earthshaker", "Sven", "Leshrac", "Underlord", "Axe"}
    hero_anti_heal = {"Ancient Apparition", "Necrophos", "Doom", "Viper"}
    hero_lockdown = {"Lion", "Shadow Shaman", "Disruptor", "Silencer"}

    role_matches = not target_role or target_role in hero_roles

    if any(enemy in illusion_heroes for enemy in enemies):
        if hero in hero_aoe:
            score += 1.4 if role_matches else 0.4
            reasons.append("Strong vs illusion heroes")

    if any(enemy in heal_heroes for enemy in enemies):
        if hero in hero_anti_heal:
            score += 1.4 if role_matches else 0.5
            reasons.append("Counters enemy sustain")

    if any(enemy in mobile_heroes for enemy in enemies):
        if hero in hero_lockdown:
            score += 1.0 if role_matches else 0.2
            reasons.append("Reliable lockdown vs mobile heroes")

    return round(score, 1), reasons

def team_needs_score(
    hero: str,
    allies: list[str],
    enemies: list[str],
    target_role: str | None = None,
    occupied_roles: list[str] | None = None,
    ally_slots=None,
) -> tuple[float, list[str]]:
    total_score = 0.0
    all_reasons: list[str] = []
    buckets: dict[str, float] = {}

    def apply(
        bucket_name: str,
        bucket_cap: float,
        score: float,
        reasons: list[str],
    ) -> None:
        nonlocal total_score, all_reasons

        applied = add_bucket_score(buckets, bucket_name, score, bucket_cap)

        if applied > 0:
            total_score += applied
            all_reasons.extend(reasons)

        elif score < 0:
            total_score += score
            all_reasons.extend(reasons)

    role_score_1, role_reasons_1 = role_balance_score(hero, allies)
    apply("role", 2.2, role_score_1, role_reasons_1)

    role_score_2, role_reasons_2 = role_preference_score(hero, target_role)
    apply("role", 2.2, role_score_2, role_reasons_2)

    role_score_3, role_reasons_3 = ally_slot_score(hero, ally_slots)
    apply("role", 2.2, role_score_3, role_reasons_3)

    frontline_bonus, frontline_reasons = frontline_score(hero, allies)
    apply("team_needs", 2.4, frontline_bonus, frontline_reasons)

    scaling_bonus, scaling_reasons = scaling_score(hero, allies)
    apply("team_needs", 2.4, scaling_bonus, scaling_reasons)

    disable_bonus, disable_reasons = disable_score(hero, allies)
    apply("team_needs", 2.4, disable_bonus, disable_reasons)

    push_bonus, push_reasons = push_score(hero, allies)
    apply("team_needs", 2.4, push_bonus, push_reasons)

    tempo_bonus, tempo_reasons = tempo_score(hero, allies)
    apply("team_needs", 2.4, tempo_bonus, tempo_reasons)

    counter_score, counter_reasons = hard_counter_priority_score(
        hero,
        enemies,
        target_role=target_role,
    )
    apply("counter", 2.0, counter_score, counter_reasons)

    anti_score, anti_reasons = anti_illusion_score(hero, enemies)
    apply("counter", 2.0, anti_score, anti_reasons)

    strategy_score, strategy_reasons = enemy_strategy_score(
        hero,
        enemies,
        target_role=target_role,
    )
    apply("counter", 2.0, strategy_score, strategy_reasons)

    save_bonus, save_reasons = save_score(hero, allies, enemies)
    apply("utility", 1.2, save_bonus, save_reasons)

    phase_bonus, phase_reasons = draft_phase_score(hero, allies, enemies)
    apply("phase", 0.8, phase_bonus, phase_reasons)

    lane_bonus, lane_reasons = lane_matchup_score(hero, enemies, allies)
    apply("lane", 1.0, lane_bonus, lane_reasons)

    return round(total_score, 1), all_reasons