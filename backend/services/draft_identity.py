TEAMFIGHT_HEROES = {
    "Mars",
    "Tidehunter",
    "Enigma",
    "Phoenix",
    "Faceless Void",
    "Magnus",
    "Warlock",
    "Dark Seer",
    "Earthshaker",
}

PUSH_HEROES = {
    "Shadow Shaman",
    "Nature's Prophet",
    "Lycan",
    "Beastmaster",
    "Dragon Knight",
    "Death Prophet",
    "Chen",
    "Broodmother",
}

PICKOFF_HEROES = {
    "Storm Spirit",
    "Puck",
    "Nyx Assassin",
    "Bounty Hunter",
    "Riki",
    "Clinkz",
    "Spirit Breaker",
    "Slark",
}

GREEDY_HEROES = {
    "Medusa",
    "Anti-Mage",
    "Spectre",
    "Arc Warden",
    "Tinker",
    "Alchemist",
}


def analyze_draft_identity(allies: list[str]) -> dict:
    strengths = []
    weaknesses = []

    teamfight = sum(hero in TEAMFIGHT_HEROES for hero in allies)
    push = sum(hero in PUSH_HEROES for hero in allies)
    pickoff = sum(hero in PICKOFF_HEROES for hero in allies)
    greedy = sum(hero in GREEDY_HEROES for hero in allies)

    if teamfight >= 2:
        strengths.append("strong teamfight")

    if push >= 2:
        strengths.append("good tower push")

    if pickoff >= 2:
        strengths.append("strong pickoff potential")

    if greedy >= 2:
        weaknesses.append("greedy draft")

    if teamfight == 0:
        weaknesses.append("weak teamfight")

    if push == 0:
        weaknesses.append("low tower damage")

    style = "Balanced"

    if teamfight >= push and teamfight >= pickoff:
        style = "Teamfight"
    elif push >= teamfight and push >= pickoff:
        style = "Push"
    elif pickoff >= teamfight and pickoff >= push:
        style = "Pickoff"

    return {
        "style": style,
        "strengths": strengths,
        "weaknesses": weaknesses,
    }