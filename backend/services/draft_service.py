from ..data.hero_attributes import HERO_ROLES
from ..engines.rule_engine import recommend_with_explanations
from .scoring import team_needs_score


def get_draft_recommendations(
    allies: list[str],
    enemies: list[str],
    k: int = 8,
) -> list[dict]:
    top_heroes, explanations = recommend_with_explanations(allies, enemies, k=15)

    recommendations: list[dict] = []

    for hero in top_heroes:
        base_info = explanations.get(hero, {})
        base_score = float(base_info.get("score", 0.0))
        base_reasons = list(base_info.get("reasons", []))

        comp_score, comp_reasons = team_needs_score(hero, allies, enemies)

        total_score = round(base_score + comp_score, 1)

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