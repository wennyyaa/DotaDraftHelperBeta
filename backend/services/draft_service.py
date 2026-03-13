from ..data.hero_attributes import HERO_ROLES
from ..engines.rule_engine import recommend_with_explanations
from .explanation_engine import summarize_reasons
from .scoring import team_needs_score


def classify_confidence(score: float) -> str:
    if score >= 5.0:
        return "best-pick"
    if score >= 3.0:
        return "strong-fit"
    if score >= 1.5:
        return "situational"
    return "risky"


def get_draft_recommendations(
        
    allies: list[str],
    enemies: list[str],
    k: int = 8,
    target_role: str | None = None,
    occupied_roles: list[str] | None = None,
) -> list[dict]:
    top_heroes, explanations = recommend_with_explanations(allies, enemies, k=30)

    recommendations: list[dict] = []

    for hero in top_heroes:
        base_info = explanations.get(hero, {})
        base_score = float(base_info.get("score", 0.0))
        base_reasons = list(base_info.get("reasons", []))

        comp_score, comp_reasons = team_needs_score(
        hero,
        allies,
        enemies,
        target_role=target_role,
        occupied_roles=occupied_roles,
)
        all_reasons = base_reasons + comp_reasons
        summary = summarize_reasons(hero, all_reasons)

        total_score = round(base_score + comp_score, 1)

        recommendations.append(
            {
                "hero": hero,
                "score": total_score,
                "reasons": all_reasons,
                "summary": summary,
                "roles": HERO_ROLES.get(hero, []),
                "confidence": classify_confidence(total_score),
            }
        )

    recommendations.sort(key=lambda x: (-x["score"], x["hero"]))

    filtered = [r for r in recommendations if r["score"] > 0]

    if filtered:
        return filtered[:k]

    return recommendations[:k]
#     for hero in top_heroes:
#         base_info = explanations.get(hero, {})
#         base_score = float(base_info.get("score", 0.0))
#         base_reasons = list(base_info.get("reasons", []))
#         phase_score = phase_adjustment(hero, phase)
        

#         comp_score, comp_reasons = team_needs_score(hero, allies, enemies)

#         total_score = round(base_score + comp_score + phase_score, 1)
        
#         all_reasons = base_reasons + comp_reasons + data_reasons

#         summary = summarize_reasons(hero, all_reasons)

#     recommendations.append(
#     {
#         "hero": hero,
#         "score": round(base_score + comp_score + data_score, 1),
#         "reasons": all_reasons,
#         "summary": summary,
#         "roles": HERO_ROLES.get(hero, []),
#     }
# )

#     recommendations.sort(key=lambda x: (-x["score"], x["hero"]))

#     filtered = [r for r in recommendations if r["score"] > 0]

#     if filtered:
#         return filtered[:k]

#     return recommendations[:k] 

