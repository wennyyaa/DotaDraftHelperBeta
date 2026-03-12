from ..data.hero_mapping import HERO_NAME_TO_OPENDOTA_ID
from ..data.opendota_client import get_hero_matchups


from ..data.hero_mapping import HERO_NAME_TO_OPENDOTA_ID
from ..data.opendota_client import get_hero_matchups
from .scoring import get_draft_phase


def matchup_score(hero: str, enemies: list[str], allies: list[str] | None = None) -> tuple[float, list[str]]:
    hero_id = HERO_NAME_TO_OPENDOTA_ID.get(hero)
    if hero_id is None:
        return 0.0, []

    try:
        matchups = get_hero_matchups(hero_id)
    except Exception:
        return 0.0, []

    by_enemy_id = {row.get("hero_id"): row for row in matchups}

    total_score = 0.0
    reasons: list[str] = []

    phase = "mid"
    if allies is not None:
        phase = get_draft_phase(allies, enemies)

    phase_multiplier = 1.0
    if phase == "late":
        phase_multiplier = 1.35
    elif phase == "early":
        phase_multiplier = 0.8

    for enemy in enemies:
        enemy_id = HERO_NAME_TO_OPENDOTA_ID.get(enemy)
        if enemy_id is None:
            continue

        row = by_enemy_id.get(enemy_id)
        if not row:
            continue

        games = row.get("games_played", 0) or 0
        wins = row.get("wins", 0) or 0

        if games < 50:
            continue

        winrate = wins / games
        delta = winrate - 0.5

        score = round(delta * 20 * phase_multiplier, 1)

        if score >= 0.8:
            total_score += score
            reasons.append(f"Strong historical matchup vs {enemy}")
        elif score <= -0.8:
            total_score += score
            reasons.append(f"Weak historical matchup vs {enemy}")

    return round(total_score, 1), reasons