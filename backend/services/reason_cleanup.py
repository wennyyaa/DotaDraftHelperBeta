from .reason_cleanup import dedupe_reasons

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

    noisy_exact_or_prefix = [
        "too many offlanes already",
        "too many supports already",
        "too many mids already",
        "too many carries already",
        "fits carry role",
        "fits mid role",
        "fits offlane role",
        "fits support role",
        "fills missing carry role",
        "fills missing mid role",
        "fills missing offlane role",
        "fills missing support role",
        "fits open carry slot",
        "fits open mid slot",
        "fits open offlane slot",
        "fits open support slot",
        "team lacks carry",
        "team lacks mid",
        "team lacks offlane",
        "team lacks support",
    ]

    if any(text.startswith(prefix) for prefix in noisy_exact_or_prefix):
        return True

    # when role is selected, hide unrelated role-clash chatter
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

    # semantic buckets so same idea does not appear 3 times
    bucket_taken = {
        "counter": False,
        "push": False,
        "disable": False,
        "save": False,
        "frontline": False,
        "scaling": False,
        "lane": False,
        "utility": False,
        "role_pick": False,
    }

    for reason in reasons:
        if is_noise_reason(reason, target_role=target_role):
            continue

        normalized = normalize_reason(reason)
        if not normalized:
            continue

        lower = normalized.lower()

        # semantic bucketing
        bucket = None

        if "counter" in lower or lower.startswith("counters "):
            bucket = "counter"
        elif "pusher" in lower or "tower" in lower or "push" in lower:
            bucket = "push"
        elif "disable" in lower or "control" in lower or "stun" in lower:
            bucket = "disable"
        elif "save" in lower:
            bucket = "save"
        elif "frontline" in lower or "tank" in lower:
            bucket = "frontline"
        elif "scaling" in lower or "late-game" in lower:
            bucket = "scaling"
        elif "lane" in lower or "matchup" in lower:
            bucket = "lane"
        elif "good carry pick" in lower or "good mid pick" in lower or "good offlane pick" in lower or "good support pick" in lower:
            bucket = "role_pick"
        elif "safe pick" in lower or "stable pick" in lower:
            bucket = "utility"

        if bucket is not None and bucket_taken[bucket]:
            continue

        if bucket is not None:
            bucket_taken[bucket] = True

        if lower not in seen:
            seen.add(lower)
            cleaned.append(normalized)

    return cleaned[:4]