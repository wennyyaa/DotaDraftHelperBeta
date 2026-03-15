def normalize_reason(reason: str) -> str:
    if not reason:
        return ""

    text = reason.strip()

    replacements = {
        "Adds tower pressure": "Good pusher",
        "Adds reliable control": "Reliable disable",
        "Provides defensive save": "Defensive save",
        "Adds frontline": "Frontline",
        "Adds late-game scaling": "Late-game scaling",
        "Fits open carry slot": "Fits carry role",
        "Fits open mid slot": "Fits mid role",
        "Fits open offlane slot": "Fits offlane role",
        "Fits open support slot": "Fits support role",
        "Fills missing carry role": "Fits carry role",
        "Fills missing mid role": "Fits mid role",
        "Fills missing offlane role": "Fits offlane role",
        "Fills missing support role": "Fits support role",
        "Preferred carry pick for this draft": "Good carry pick",
        "Preferred mid pick for this draft": "Good mid pick",
        "Preferred offlane pick for this draft": "Good offlane pick",
        "Preferred support pick for this draft": "Good support pick",
        "Preferred hard_support pick for this draft": "Good support pick",
        "Safe and flexible early pick": "Safe pick",
        "Stable mid-draft option": "Stable pick",
    }

    return replacements.get(text, text)


def is_noise_reason(reason: str, target_role: str | None = None) -> bool:
    if not reason:
        return True

    text = reason.lower().strip()

    noisy_prefixes = [
        "too many offlanes already",
        "too many supports already",
        "too many mids already",
        "too many carries already",
    ]

    if any(text.startswith(prefix) for prefix in noisy_prefixes):
        return True

    if target_role:
        unrelated = {
            "carry": ["offlane", "support", "mid"],
            "mid": ["offlane", "support", "carry"],
            "offlane": ["mid", "support", "carry"],
            "support": ["mid", "offlane", "carry"],
            "hard_support": ["mid", "offlane", "carry"],
        }

        for other_role in unrelated.get(target_role, []):
            if f"too many {other_role}" in text:
                return True

    return False


def dedupe_reasons(reasons: list[str], target_role: str | None = None) -> list[str]:
    cleaned: list[str] = []
    seen = set()

    role_bucket_taken = False

    for reason in reasons:
        if is_noise_reason(reason, target_role=target_role):
            continue

        normalized = normalize_reason(reason)
        if not normalized:
            continue

        lower = normalized.lower()

        role_bucket_markers = [
            "fits carry role",
            "fits mid role",
            "fits offlane role",
            "fits support role",
            "good carry pick",
            "good mid pick",
            "good offlane pick",
            "good support pick",
            "team lacks carry",
            "team lacks mid",
            "team lacks offlane",
            "team lacks support",
        ]

        if any(marker in lower for marker in role_bucket_markers):
            if role_bucket_taken:
                continue
            role_bucket_taken = True

            if "team lacks" in lower:
                continue

        if lower not in seen:
            seen.add(lower)
            cleaned.append(normalized)

    return cleaned[:4]