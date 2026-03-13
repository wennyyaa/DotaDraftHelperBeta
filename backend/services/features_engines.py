from ..data.hero_attributes import (
    DISABLE_HEROES,
    FRONTLINE_HEROES,
    HERO_SCALING,
    PUSH_HEROES,
    SAVE_HEROES,
)
from ..data.hero_features import HERO_FEATURES


def _default_features(hero: str) -> dict:
    """
    Build a fallback feature set for heroes that do not yet have
    a hand-crafted entry in HERO_FEATURES.
    """

    frontline = 1 if hero in FRONTLINE_HEROES else 0
    control = 1 if hero in DISABLE_HEROES else 0
    push = 1 if hero in PUSH_HEROES else 0
    scaling = 1 if HERO_SCALING.get(hero) == "late" else 0
    save = 1 if hero in SAVE_HEROES else 0

    # simple baseline approximation:
    # if a hero has control + frontline, or strong control alone,
    # they usually contribute meaningfully to teamfights
    teamfight = 1 if (control == 1 or frontline == 1) else 0

    return {
        "frontline": frontline,
        "control": control,
        "teamfight": teamfight,
        "scaling": scaling,
        "push": push,
        "save": save,
    }


def get_hero_features(hero: str) -> dict:
    """
    Return hero features.
    Prefer manual feature definitions, but always fall back to a derived baseline.
    """

    if hero in HERO_FEATURES:
        return HERO_FEATURES[hero]

    return _default_features(hero)


def team_feature_summary(heroes: list[str]) -> dict:
    """
    Aggregate gameplay features for a whole team.
    """

    summary = {
        "frontline": 0,
        "control": 0,
        "teamfight": 0,
        "scaling": 0,
        "push": 0,
        "save": 0,
    }

    for hero in heroes:
        features = get_hero_features(hero)

        for key in summary:
            summary[key] += features.get(key, 0)

    return summary