from .features_engines import team_feature_summary


def infer_draft_archetype(allies: list[str]) -> tuple[str, list[str]]:
    """
    Infer the current ally draft style from team features.
    Returns:
        archetype name,
        short reasons
    """

    summary = team_feature_summary(allies)

    reasons: list[str] = []

    if summary["push"] >= 2:
        reasons.append("push")

    if summary["teamfight"] >= 2:
        reasons.append("teamfight")

    if summary["scaling"] >= 2:
        reasons.append("late-game")

    if summary["control"] >= 2 and summary["teamfight"] <= 1:
        reasons.append("pickoff")

    if not reasons:
        return "balanced", ["balanced"]

    if "teamfight" in reasons and "push" in reasons:
        return "siege-teamfight", reasons

    if "late-game" in reasons and len(reasons) == 1:
        return "greedy-scaling", reasons

    if "pickoff" in reasons and len(reasons) == 1:
        return "pickoff", reasons

    if "push" in reasons and len(reasons) == 1:
        return "push", reasons

    if "teamfight" in reasons and len(reasons) == 1:
        return "teamfight", reasons

    return "hybrid", reasons


def archetype_score(hero: str, allies: list[str], hero_features: dict) -> tuple[float, list[str]]:
    """
    Reward heroes that fit the current draft archetype.
    """

    archetype, _ = infer_draft_archetype(allies)

    score = 0.0
    reasons: list[str] = []

    if archetype == "teamfight":
        if hero_features.get("teamfight", 0) == 1:
            score += 0.8
            reasons.append("Fits your teamfight composition")

    elif archetype == "push":
        if hero_features.get("push", 0) == 1:
            score += 0.8
            reasons.append("Completes push-oriented draft")

    elif archetype == "pickoff":
        if hero_features.get("control", 0) == 1:
            score += 0.7
            reasons.append("Supports pickoff strategy")

    elif archetype == "greedy-scaling":
        if hero_features.get("scaling", 0) == 1:
            score += 0.8
            reasons.append("Strengthens late-game identity")

    elif archetype == "siege-teamfight":
        if hero_features.get("push", 0) == 1 or hero_features.get("teamfight", 0) == 1:
            score += 0.7
            reasons.append("Fits your siege and teamfight style")

    elif archetype == "hybrid":
        if hero_features.get("teamfight", 0) == 1 or hero_features.get("control", 0) == 1:
            score += 0.5
            reasons.append("Fits your flexible draft style")

    return round(score, 1), reasons