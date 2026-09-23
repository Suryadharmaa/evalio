"""Contract for the optional semantic essay review."""

from typing import Literal

from pydantic import Field

from api.admission_engine.schemas.common import ApiModel

CategoryName = Literal[
    "content", "structure", "voice", "specificity", "reflection", "writing_quality"
]
RUBRIC: dict[str, int] = {
    "content": 20,
    "structure": 15,
    "voice": 20,
    "specificity": 15,
    "reflection": 20,
    "writing_quality": 10,
}


class EssayReviewRequest(ApiModel):
    essay: str = Field(min_length=1, max_length=50_000)
    refresh: bool = False


class DeepReviewRequest(ApiModel):
    analysis_id: str = Field(min_length=1, max_length=80)
    essay: str = Field(min_length=1, max_length=50_000)


class CategoryReview(ApiModel):
    score: int = Field(ge=0)
    max_score: int = Field(ge=1)
    feedback: str = Field(min_length=1, max_length=300)


class SemanticReview(ApiModel):
    overall_impression: str = Field(min_length=1, max_length=320)
    categories: dict[CategoryName, CategoryReview]
    strengths: list[str] = Field(max_length=4)
    improvements: list[str] = Field(max_length=4)
    priority_action: str = Field(min_length=1, max_length=240)
    confidence: float = Field(ge=0, le=1)

    def validated_score(self) -> int:
        if set(self.categories) != set(RUBRIC):
            raise ValueError("Semantic review must return all six categories")
        for name, maximum in RUBRIC.items():
            category = self.categories[name]  # type: ignore[index]
            if category.max_score != maximum or category.score > maximum:
                raise ValueError(f"Invalid score for {name}")
        return sum(item.score for item in self.categories.values())


class DeepReview(ApiModel):
    strongest_paragraph: int = Field(ge=1)
    weakest_paragraph: int = Field(ge=1)
    opening: str = Field(min_length=1, max_length=300)
    conclusion: str = Field(min_length=1, max_length=300)
    narrative_arc: str = Field(min_length=1, max_length=300)
    paragraph_feedback: list[str] = Field(min_length=1, max_length=24)
    revision_priorities: list[str] = Field(min_length=1, max_length=4)
