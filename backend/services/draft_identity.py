from .archetype_engine import infer_draft_archetype
from .features_engines import team_feature_summary


def build_draft_identity(allies: list[str]) -> dict:
    """
    Build a readable draft identity summary for the allied team.
    """

    archetype, _ = infer_draft_archetype(allies)
    summary = team_feature_summary(allies)

    strengths: list[str] = []
    weaknesses: list[str] = []

    if summary["frontline"] >= 2:
        strengths.append("Strong frontline")
    elif summary["frontline"] == 0:
        weaknesses.append("Low frontline")

    if summary["control"] >= 2:
        strengths.append("Strong control")
    elif summary["control"] == 0:
        weaknesses.append("Low control")

    if summary["teamfight"] >= 2:
        strengths.append("Strong teamfight")
    elif summary["teamfight"] == 0:
        weaknesses.append("Weak teamfight")

    if summary["push"] >= 2:
        strengths.append("Good tower pressure")
    elif summary["push"] == 0:
        weaknesses.append("Low push")

    if summary["scaling"] >= 2:
        strengths.append("Strong late game")
    elif summary["scaling"] == 0:
        weaknesses.append("Weak scaling")

    if summary["save"] >= 1:
        strengths.append("Defensive utility")

    if not strengths:
        strengths.append("Balanced structure")

    if not weaknesses:
        weaknesses.append("No major weaknesses detected")

    pretty_archetype = {
        "teamfight": "Teamfight",
        "push": "Push",
        "pickoff": "Pickoff",
        "greedy-scaling": "Greedy Scaling",
        "siege-teamfight": "Siege + Teamfight",
        "hybrid": "Hybrid",
        "balanced": "Balanced",
    }.get(archetype, "Balanced")

    return {
        "style": pretty_archetype,
        "strengths": strengths[:3],
        "weaknesses": weaknesses[:3],
    }