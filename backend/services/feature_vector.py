from ..data.hero_attributes import (
    DISABLE_HEROES,
    FRONTLINE_HEROES,
    HERO_ROLES,
    HERO_SCALING,
    PUSH_HEROES,
    SAVE_HEROES,
)
from .enemy_strategy import detect_enemy_strategy
from .slot_features import extract_slot_features


def build_feature_vector(
    hero: str,
    allies: list[str],
    enemies: list[str],
    target_role: str | None = None,
    ally_slots=None,
) -> dict[str, int | float | str]:
    """
    Build a ML-friendly feature dictionary for one candidate hero
    in the current draft state.
    """

    features: dict[str, int | float | str] = {}

    hero_roles = HERO_ROLES.get(hero, [])

    # -------------------------
    # Candidate hero identity / role features
    # -------------------------
    features["candidate_hero"] = hero
    features["candidate_is_carry"] = int("carry" in hero_roles)
    features["candidate_is_mid"] = int("mid" in hero_roles)
    features["candidate_is_offlane"] = int("offlane" in hero_roles)
    features["candidate_is_support"] = int("support" in hero_roles)
    features["candidate_is_hard_support"] = int("hard_support" in hero_roles)

    features["candidate_frontline"] = int(hero in FRONTLINE_HEROES)
    features["candidate_disable"] = int(hero in DISABLE_HEROES)
    features["candidate_push"] = int(hero in PUSH_HEROES)
    features["candidate_save"] = int(hero in SAVE_HEROES)
    features["candidate_late_scaling"] = int(HERO_SCALING.get(hero) == "late")

    # -------------------------
    # Ally team features
    # -------------------------
    features["ally_count"] = len(allies)
    features["ally_frontliners"] = sum(1 for h in allies if h in FRONTLINE_HEROES)
    features["ally_disable_count"] = sum(1 for h in allies if h in DISABLE_HEROES)
    features["ally_push_count"] = sum(1 for h in allies if h in PUSH_HEROES)
    features["ally_save_count"] = sum(1 for h in allies if h in SAVE_HEROES)
    features["ally_late_scaling_count"] = sum(
        1 for h in allies if HERO_SCALING.get(h) == "late"
    )

    # ally role counts
    features["ally_carry_count"] = sum(
        1 for h in allies if "carry" in HERO_ROLES.get(h, [])
    )
    features["ally_mid_count"] = sum(
        1 for h in allies if "mid" in HERO_ROLES.get(h, [])
    )
    features["ally_offlane_count"] = sum(
        1 for h in allies if "offlane" in HERO_ROLES.get(h, [])
    )
    features["ally_support_count"] = sum(
        1 for h in allies if "support" in HERO_ROLES.get(h, [])
    )
    features["ally_hard_support_count"] = sum(
        1 for h in allies if "hard_support" in HERO_ROLES.get(h, [])
    )

    # -------------------------
    # Enemy team features
    # -------------------------
    features["enemy_count"] = len(enemies)
    features["enemy_frontliners"] = sum(1 for h in enemies if h in FRONTLINE_HEROES)
    features["enemy_disable_count"] = sum(1 for h in enemies if h in DISABLE_HEROES)
    features["enemy_push_count"] = sum(1 for h in enemies if h in PUSH_HEROES)
    features["enemy_save_count"] = sum(1 for h in enemies if h in SAVE_HEROES)
    features["enemy_late_scaling_count"] = sum(
        1 for h in enemies if HERO_SCALING.get(h) == "late"
    )

    # -------------------------
    # Enemy strategy features
    # -------------------------
    enemy_strategies = detect_enemy_strategy(enemies)

    features["enemy_strategy_illusion"] = int("illusion" in enemy_strategies)
    features["enemy_strategy_zoo"] = int("zoo" in enemy_strategies)
    features["enemy_strategy_mobile"] = int("mobile" in enemy_strategies)
    features["enemy_strategy_sustain"] = int("sustain" in enemy_strategies)

    # -------------------------
    # Draft phase features
    # -------------------------
    total_picks = len(allies) + len(enemies)

    features["draft_total_picks"] = total_picks
    features["draft_phase_early"] = int(total_picks <= 3)
    features["draft_phase_mid"] = int(4 <= total_picks <= 6)
    features["draft_phase_late"] = int(total_picks >= 7)

    # -------------------------
    # Requested role features
    # -------------------------
    features["target_role_carry"] = int(target_role == "carry")
    features["target_role_mid"] = int(target_role == "mid")
    features["target_role_offlane"] = int(target_role == "offlane")
    features["target_role_support"] = int(target_role == "support")
    features["target_role_hard_support"] = int(target_role == "hard_support")

    features["candidate_matches_target_role"] = int(
        bool(target_role) and target_role in hero_roles
    )

    # -------------------------
    # Explicit ally slot features
    # -------------------------
    slot_features = extract_slot_features(ally_slots)
    for key, value in slot_features.items():
        features[f"ally_slots_{key}"] = value

    return features