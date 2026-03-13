def summarize_reasons(hero: str, reasons: list[str]) -> str:
    if not reasons:
        return ""

    text = " ".join(reasons).lower()

    if "huskar" in text:
        return "Special answer to Huskar"

    if "frontline" in text:
        return "Strong frontline option for this draft"

    if "teamfight" in text:
        return "Adds powerful teamfight presence"

    if "scaling" in text:
        return "Strong late-game scaling core"

    if "control" in text:
        return "Provides reliable control"

    if "push" in text or "objective" in text:
        return "Adds objective pressure"

    return "Solid pick for current draft"