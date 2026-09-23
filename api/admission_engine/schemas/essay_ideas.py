from typing import Literal

from pydantic import Field, field_validator, model_validator

from api.admission_engine.schemas.common import ApiModel

EssayIdeaType = Literal["COMMON_APP", "SUPPLEMENTAL", "SCHOLARSHIP", "OTHER"]


class EssayIdeaBuildRequest(ApiModel):
    essay_type: EssayIdeaType = "COMMON_APP"
    prompt_selection: str | None = Field(default=None, max_length=500)
    experiences: list[str] = Field(default_factory=list, max_length=12)
    activities: list[str] = Field(default_factory=list, max_length=12)
    values: list[str] = Field(default_factory=list, max_length=12)
    challenges: list[str] = Field(default_factory=list, max_length=12)
    turning_points: list[str] = Field(default_factory=list, max_length=12)
    specific_moments: list[str] = Field(default_factory=list, max_length=12)
    people_or_places: list[str] = Field(default_factory=list, max_length=12)
    lessons_or_changes: list[str] = Field(default_factory=list, max_length=12)

    @field_validator(
        "experiences",
        "activities",
        "values",
        "challenges",
        "turning_points",
        "specific_moments",
        "people_or_places",
        "lessons_or_changes",
    )
    @classmethod
    def normalize_items(cls, items: list[str]) -> list[str]:
        normalized: list[str] = []
        seen: set[str] = set()
        for item in items:
            clean = " ".join(item.split())
            if not clean:
                continue
            if len(clean) > 500:
                raise ValueError("idea inputs may contain at most 500 characters each")
            key = clean.casefold()
            if key not in seen:
                normalized.append(clean)
                seen.add(key)
        return normalized

    @field_validator("prompt_selection")
    @classmethod
    def normalize_prompt(cls, value: str | None) -> str | None:
        clean = " ".join(value.split()) if value else ""
        return clean or None

    @model_validator(mode="after")
    def require_grounded_combinations(self) -> "EssayIdeaBuildRequest":
        anchors = self.specific_moments + self.experiences + self.activities
        tensions = self.challenges + self.turning_points
        if not anchors:
            raise ValueError("add at least one specific moment, experience, or activity")
        if not tensions:
            raise ValueError("add at least one challenge or turning point")
        if not self.values:
            raise ValueError("add at least one core value")
        if not self.lessons_or_changes:
            raise ValueError("add at least one lesson or change")
        combinations = len(anchors) * len(tensions) * len(self.values) * len(self.lessons_or_changes)
        if combinations < 3:
            raise ValueError("add enough distinct inputs to create at least three grounded directions")
        return self


class EssayIdeaDirection(ApiModel):
    idea_number: int
    title: str
    moment: str
    tension: str
    core_value: str
    change: str
    reflection_direction: str
    people_or_place: str | None = None
    possible_fit: str
    questions_to_explore: list[str]
    source_indices: dict[str, int]


class EssayIdeaBuildResponse(ApiModel):
    engine_version: str = "2.0.0"
    builder_version: str = "idea-builder-1.0.0"
    ideas: list[EssayIdeaDirection] = Field(min_length=3, max_length=8)
