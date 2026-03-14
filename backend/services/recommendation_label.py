def infer_recommendation_label(
    hero: str,
    reasons: list[str],
    confidence: str,
    roles: list[str],
) -> str:
    joined = " | ".join(reasons).lower()

    if "strong counter" in joined or "counters enemy" in joined or "special answer" in joined:
        return "Counter Pick"

    if "safe and flexible early pick" in joined or "stable mid-draft option" in joined:
        return "Safe Pick"

    if "provides defensive save" in joined or "adds reliable control" in joined:
        return "Utility Pick"

    if "late-game scaling" in joined or "too greedy" in joined or "greedy" in joined:
        return "Greedy Option"

    if confidence == "best-pick":
        return "Best Fit"

    if "support" in roles and "Preferred support pick for this draft".lower() in joined:
        return "Best Support Fit"

    if "carry" in roles and "Preferred carry pick for this draft".lower() in joined:
        return "Best Carry Fit"

    return "Strong Pick"