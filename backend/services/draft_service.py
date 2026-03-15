from ..data.hero_attributes import HERO_ROLES
from ..engines.rule_engine import recommend_with_explanations
from ..ml.predict_model import ml_score_bonus

from .scoring import team_needs_score
from .explanation_engine import summarize_reasons
from .recommendation_label import infer_recommendation_label
from .reason_cleanup import dedupe_reasons









def normalize_role(role: str | None) -> str | None:
    if role == "hard_support":
        return "support"
    return role






def classify_confidence(score: float) -> str:
    if score >= 5.0:
        return "best-pick"

    if score >= 3.0:
        return "strong-fit"

    if score >= 1.5:
        return "situational"

    return "risky"


# ----------------------------
# Candidate pool builder
# ----------------------------

def build_candidate_pool(
    allies: list[str],
    enemies: list[str],
    target_role: str | None = None,
) -> tuple[list[str], dict]:

    target_role = normalize_role(target_role)

    top_heroes, explanations = recommend_with_explanations(
        allies,
        enemies,
        k=80,
    )

    banned = set(allies) | set(enemies)

    if not target_role:
        return top_heroes, explanations

    role_heroes = [
        hero
        for hero, roles in HERO_ROLES.items()
        if target_role in roles and hero not in banned
    ]

    seen = set()
    candidate_pool: list[str] = []

    for hero in role_heroes:
        if hero not in seen:
            seen.add(hero)
            candidate_pool.append(hero)

    for hero in top_heroes:
        if hero in banned:
            continue

        if hero not in seen:
            seen.add(hero)
            candidate_pool.append(hero)

    return candidate_pool, explanations


# ----------------------------
# Main recommendation engine
# ----------------------------

def get_draft_recommendations(
    
    allies: list[str],
    enemies: list[str],
    k: int = 8,
    target_role: str | None = None,
    occupied_roles: list[str] | None = None,
    ally_slots=None,
) -> list[dict]:

    target_role = normalize_role(target_role)

    candidate_pool, explanations = build_candidate_pool(
        allies,
        enemies,
        target_role=target_role,
    )

    recommendations: list[dict] = []

    for hero in candidate_pool:

        base_info = explanations.get(hero, {})

        base_score = float(base_info.get("score", 0.0))
        base_reasons = list(base_info.get("reasons", []))

        comp_score, comp_reasons = team_needs_score(
            hero,
            allies,
            enemies,
            target_role=target_role,
            occupied_roles=occupied_roles,
            ally_slots=ally_slots,
        )

        ml_score = 0.0
        ml_reasons = []

        total_score = round(base_score + comp_score + ml_score, 1)

        raw_reasons = base_reasons + comp_reasons + ml_reasons
        all_reasons = dedupe_reasons(raw_reasons, target_role=target_role)

        summary = summarize_reasons(hero, all_reasons)

        confidence = classify_confidence(total_score)

        roles = HERO_ROLES.get(hero, [])

        label = infer_recommendation_label(
            hero=hero,
            reasons=all_reasons,
            confidence=confidence,
            roles=roles,
        )

        recommendations.append(
            {
                "hero": hero,
                "score": total_score,
                "reasons": all_reasons,
                "summary": summary,
                "roles": roles,
                "confidence": confidence,
                "label": label,
            }
        )

    recommendations.sort(key=lambda x: (-x["score"], x["hero"]))

    filtered = [r for r in recommendations if r["score"] > 0]

    final_pool = filtered if filtered else recommendations

    if target_role:

        role_fit = [
            r for r in final_pool
            if target_role in r.get("roles", [])
        ]

        off_role = [
            r for r in final_pool
            if target_role not in r.get("roles", [])
        ]

        role_fit.sort(key=lambda x: (-x["score"], x["hero"]))
        off_role.sort(key=lambda x: (-x["score"], x["hero"]))

        if len(role_fit) >= k:
            return role_fit[:k]

        return (role_fit + off_role)[:k]

    return final_pool[:k]