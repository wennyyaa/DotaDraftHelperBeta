# backend/tests/draft_cases.py

DRAFT_CASES = [
    {
        "name": "Anti Huskar basics",
        "allies": ["Mars", "Phoenix"],
        "enemies": ["Huskar"],
        "target_role": None,
        "occupied_roles": [],
        "expected_any": ["Ancient Apparition", "Necrophos", "Viper"],
    },
    {
        "name": "Need carry",
        "allies": ["Mars", "Rubick", "Snapfire"],
        "enemies": ["Tidehunter"],
        "target_role": "carry",
        "occupied_roles": ["mid", "support"],
        "expected_any": [
    "Juggernaut",
    "Luna",
    "Sven",
    "Wraith King",
    "Bloodseeker",
    "Chaos Knight",
    "Clinkz",
    "Alchemist"
]
    },
    {
        "name": "Need offlane",
        "allies": ["Drow Ranger", "Oracle"],
        "enemies": ["Storm Spirit"],
        "target_role": "offlane",
        "occupied_roles": ["carry", "support"],
        "expected_any": ["Centaur Warrunner", "Mars", "Underlord", "Slardar"],
    },
    {
        "name": "Enemy illusions",
        "allies": ["Puck", "Mars"],
        "enemies": ["Phantom Lancer"],
        "target_role": None,
        "occupied_roles": [],
        "expected_any": ["Earthshaker", "Sven", "Leshrac", "Underlord", "Axe"],
    },
    {
        "name": "Save support needed",
        "allies": ["Puck", "Mars"],
        "enemies": ["Legion Commander", "Lion"],
        "target_role": "support",
        "occupied_roles": ["mid", "offlane"],
        "expected_any": ["Oracle", "Dazzle", "Abaddon", "Shadow Demon"],
    },
    {
        "name": "Greedy draft should still find frontline",
        "allies": ["Medusa", "Rubick", "Silencer"],
        "enemies": ["Axe"],
        "target_role": "offlane",
        "occupied_roles": ["carry", "support"],
        "expected_any": ["Mars", "Centaur Warrunner", "Underlord", "Tidehunter"],
    },
    {
        "name": "Push archetype support fit",
        "allies": ["Death Prophet", "Beastmaster"],
        "enemies": ["Puck"],
        "target_role": "support",
        "occupied_roles": ["mid", "offlane"],
        "expected_any": ["Shadow Shaman", "Jakiro", "Snapfire"],
    },
]