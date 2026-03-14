from typing import List, Optional, Set

from pydantic import BaseModel, Field, field_validator, model_validator

from .heroes import HERO_SET


class TeamRoles(BaseModel):
    carry: Optional[str] = None
    mid: Optional[str] = None
    offlane: Optional[str] = None
    support: Optional[str] = None
    hard_support: Optional[str] = None


class DraftRequest(BaseModel):
    allies: List[str] = Field(default_factory=list)
    enemies: List[str] = Field(default_factory=list)
    target_role: Optional[str] = None
    occupied_roles: List[str] = Field(default_factory=list)

    ally_slots: Optional[TeamRoles] = None
    enemy_slots: Optional[TeamRoles] = None

    @field_validator("allies", "enemies")
    @classmethod
    def validate_hero_names(cls, v: List[str]) -> List[str]:
        if not isinstance(v, list):
            raise TypeError("Value must be a list of hero names.")

        cleaned: List[str] = []
        for name in v:
            if not isinstance(name, str):
                raise TypeError("Each hero name must be a string.")

            hero = name.strip()

            if not hero:
                raise ValueError("Hero names cannot be empty.")

            if hero not in HERO_SET:
                raise ValueError(f"Unknown hero name: '{hero}'.")

            cleaned.append(hero)

        return cleaned

    @field_validator("target_role")
    @classmethod
    def validate_target_role(cls, v: Optional[str]) -> Optional[str]:
        allowed = {"carry", "mid", "offlane", "support", "hard_support", None}

        if v not in allowed:
            raise ValueError(
                "target_role must be one of: carry, mid, offlane, support, hard_support"
            )

        return v

    @field_validator("occupied_roles")
    @classmethod
    def validate_occupied_roles(cls, v: List[str]) -> List[str]:
        allowed = {"carry", "mid", "offlane", "support", "hard_support"}

        for role in v:
            if role not in allowed:
                raise ValueError("occupied_roles contains invalid role")

        return v

    @model_validator(mode="after")
    def validate_no_duplicates_across_teams(self) -> "DraftRequest":
   
   
        dupes: Set[str] = set()

        ally_set = set(self.allies)
        enemy_set = set(self.enemies)

        # direct duplicates across allies/enemies
        overlap = ally_set.intersection(enemy_set)
        dupes.update(overlap)

        # validate ally_slots only reference heroes already present in allies
        if self.ally_slots:
            for hero in self.ally_slots.model_dump().values():
                if hero and hero not in ally_set:
                    raise ValueError(
                        f"Ally slot hero '{hero}' must already be present in allies list."
                    )

        # validate enemy_slots only reference heroes already present in enemies
        if self.enemy_slots:
            for hero in self.enemy_slots.model_dump().values():
                if hero and hero not in enemy_set:
                    raise ValueError(
                        f"Enemy slot hero '{hero}' must already be present in enemies list."
                    )

        if dupes:
            dupes_str = ", ".join(sorted(dupes))
            raise ValueError(
                f"Duplicate hero(es) across allies/enemies: {dupes_str}. "
                "Each hero may only appear on one team."
            )

        return self


class DraftRecommendation(BaseModel):
    hero: str
    score: float
    reasons: List[str]
    summary: str = ""
    roles: List[str] = Field(default_factory=list)
    confidence: str = "low"
    label: str = ""


class DraftIdentity(BaseModel):
    style: str = "Balanced"
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)

class DraftNeeds(BaseModel):
    needs: List[str] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)

class DraftResponse(BaseModel):
    recommended: List[DraftRecommendation]
    identity: DraftIdentity
    draft_needs: DraftNeeds