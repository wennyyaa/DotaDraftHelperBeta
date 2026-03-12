from typing import List, Set

from pydantic import BaseModel, Field, field_validator, model_validator

from .heroes import HERO_SET


class DraftRequest(BaseModel):
    allies: List[str] = Field(default_factory=list)
    enemies: List[str] = Field(default_factory=list)

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

    @model_validator(mode="after")
    def validate_no_duplicates_across_teams(self) -> "DraftRequest":
        seen: Set[str] = set()
        dupes: Set[str] = set()

        for hero in self.allies + self.enemies:
            if hero in seen:
                dupes.add(hero)
            seen.add(hero)

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
    roles: List[str] = Field(default_factory=list)
    confidence: str = "low"


class DraftResponse(BaseModel):
    recommended: List[DraftRecommendation]