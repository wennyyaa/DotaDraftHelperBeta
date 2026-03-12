from ..data.hero_attributes import HERO_ROLES
from ..engines.rule_engine import recommend_with_explanations
from .scoring import team_needs_score

def get_draft_phase(allies, enemies):
    total = len(allies) + len(enemies)

    if total <= 2:
        return "early"

    if total <= 6:
        return "mid"

    return "late"

SAFE_FIRST_PICK = {
    "Puck",
    "Snapfire",
    "Tiny",
    "Abaddon",
    "Rubick",
    "Mirana",
    "Mars",
    "Dragon Knight",
}

COUNTER_HEAVY = {
    "Ancient Apparition",
    "Necrophos",
    "Viper",
}


def get_draft_phase(allies, enemies):
    total = len(allies) + len(enemies)

    if total <= 2:
        return "early"

    if total <= 6:
        return "mid"

    return "late"


def phase_adjustment(hero, phase):
    if phase == "early":
        if hero in SAFE_FIRST_PICK:
            return 1.0
        if hero in COUNTER_HEAVY:
            return -0.5

    if phase == "late":
        if hero in COUNTER_HEAVY:
            return 1.0

    return 0.0


def get_draft_recommendations(
    
    allies: list[str],
    enemies: list[str],
    k: int = 8,
) -> list[dict]:
    top_heroes, explanations = recommend_with_explanations(allies, enemies, k=15)

    recommendations: list[dict] = []
    phase = get_draft_phase(allies, enemies)
    
    for hero in top_heroes:
        base_info = explanations.get(hero, {})
        base_score = float(base_info.get("score", 0.0))
        base_reasons = list(base_info.get("reasons", []))
        phase_score = phase_adjustment(hero, phase)
        

        comp_score, comp_reasons = team_needs_score(hero, allies, enemies)

        total_score = round(base_score + comp_score + phase_score, 1)

        recommendations.append(
            {
                "hero": hero,
                "score": total_score,
                "reasons": base_reasons + comp_reasons,
                "roles": HERO_ROLES.get(hero, []),
                "confidence": (
                    "high"
                    if total_score >= 4.0
                    else "medium"
                    if total_score >= 2.0
                    else "low"
                ),
            }
        )

    recommendations.sort(key=lambda x: (-x["score"], x["hero"]))

    filtered = [r for r in recommendations if r["score"] > 0]

    if filtered:
        return filtered[:k]

    return recommendations[:k] 