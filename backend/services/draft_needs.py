from .features_engines import team_feature_summary


def analyze_draft_needs(allies: list[str]) -> dict:
    summary = team_feature_summary(allies)

    needs: list[str] = []
    notes: list[str] = []

    if summary["frontline"] == 0:
        needs.append("frontline")

    if summary["control"] <= 1:
        needs.append("reliable disable")

    if summary["push"] == 0:
        needs.append("tower damage")

    if summary["save"] == 0:
        notes.append("no defensive save")

    if summary["scaling"] == 0:
        notes.append("low late-game scaling")

    if summary["frontline"] >= 2:
        notes.append("frontline already covered")

    if summary["control"] >= 3:
        notes.append("control already covered")

    return {
        "needs": needs,
        "notes": notes,
    }