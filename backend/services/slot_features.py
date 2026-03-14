from ..models import TeamRoles


def extract_slot_features(slots: TeamRoles | None) -> dict[str, int]:
    """
    Convert ally role slots into ML-friendly binary features.
    support + hard_support are merged into one support category.
    """

    if not slots:
        return {
            "has_carry": 0,
            "has_mid": 0,
            "has_offlane": 0,
            "has_support": 0,
            "filled_roles": 0,
        }

    data = slots.model_dump()

    has_carry = 1 if data.get("carry") else 0
    has_mid = 1 if data.get("mid") else 0
    has_offlane = 1 if data.get("offlane") else 0
    has_support = 1 if data.get("support") or data.get("hard_support") else 0

    filled_roles = (
        has_carry
        + has_mid
        + has_offlane
        + has_support
    )

    return {
        "has_carry": has_carry,
        "has_mid": has_mid,
        "has_offlane": has_offlane,
        "has_support": has_support,
        "filled_roles": filled_roles,
    }


def slot_missing_roles(slots: TeamRoles | None) -> list[str]:
    """
    Return missing logical roles.
    support + hard_support are treated as support.
    """

    if not slots:
        return ["carry", "mid", "offlane", "support"]

    data = slots.model_dump()
    missing = []

    if not data.get("carry"):
        missing.append("carry")

    if not data.get("mid"):
        missing.append("mid")

    if not data.get("offlane"):
        missing.append("offlane")

    if not data.get("support") and not data.get("hard_support"):
        missing.append("support")

    return missing