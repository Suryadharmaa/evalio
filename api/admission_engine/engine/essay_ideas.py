from itertools import islice, product

from api.admission_engine.schemas.essay_ideas import (
    EssayIdeaBuildRequest,
    EssayIdeaBuildResponse,
    EssayIdeaDirection,
)

DEFAULT_FITS = {
    "COMMON_APP": "Common App — compare with your selected prompt",
    "SUPPLEMENTAL": "Supplemental essay — verify against the college prompt",
    "SCHOLARSHIP": "Scholarship essay — verify against the award prompt",
    "OTHER": "Other essay — verify against the original prompt",
}


def _title(moment: str) -> str:
    compact = moment.rstrip(".!?")
    return compact if len(compact) <= 72 else f"{compact[:69].rstrip()}…"


def build_essay_ideas(request: EssayIdeaBuildRequest) -> EssayIdeaBuildResponse:
    anchors = request.specific_moments + request.experiences + request.activities
    tensions = request.challenges + request.turning_points
    combinations = product(
        enumerate(anchors),
        enumerate(tensions),
        enumerate(request.values),
        enumerate(request.lessons_or_changes),
    )
    possible_fit = request.prompt_selection or DEFAULT_FITS[request.essay_type]
    ideas: list[EssayIdeaDirection] = []

    for idea_index, combination in enumerate(islice(combinations, 8), 1):
        (anchor_index, moment), (tension_index, tension), (value_index, value), (change_index, change) = combination
        place = request.people_or_places[(idea_index - 1) % len(request.people_or_places)] if request.people_or_places else None
        questions = [
            f"What exactly happened during “{moment}”?",
            f"What made “{tension}” difficult or uncertain?",
            f"What concrete evidence shows the change: “{change}”?",
            f"How did this experience reshape your understanding of {value}?",
        ]
        if place:
            questions.insert(1, f"How did {place} affect what happened?")
        ideas.append(
            EssayIdeaDirection(
                idea_number=idea_index,
                title=_title(moment),
                moment=moment,
                tension=tension,
                core_value=value,
                change=change,
                reflection_direction=f"Explore how your understanding of {value} changed through this experience.",
                people_or_place=place,
                possible_fit=possible_fit,
                questions_to_explore=questions,
                source_indices={
                    "anchor": anchor_index,
                    "tension": tension_index,
                    "value": value_index,
                    "change": change_index,
                },
            )
        )
    return EssayIdeaBuildResponse(ideas=ideas)
