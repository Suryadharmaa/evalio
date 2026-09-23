from api.admission_engine.schemas.profile_strength import (
    ProfileStrengthRequest,
    ProfileStrengthResponse,
)

WEIGHTS = {
    "academics": 0.35,
    "activities": 0.25,
    "honors": 0.10,
    "essay_signals": 0.15,
    "lor_signals": 0.10,
    "testing": 0.05,
}


def evaluate_profile_strength(request: ProfileStrengthRequest) -> ProfileStrengthResponse:
    components = request.model_dump()
    available_weight = sum(WEIGHTS[name] for name, value in components.items() if value is not None)
    if available_weight == 0:
        return ProfileStrengthResponse(
            score=None, display_score=None, components=components, effective_weights={}
        )
    effective = {
        name: round(weight / available_weight, 6)
        for name, weight in WEIGHTS.items()
        if components[name] is not None
    }
    score = round(sum(float(components[name]) * weight for name, weight in effective.items()), 2)
    return ProfileStrengthResponse(
        score=score, display_score=round(score), components=components, effective_weights=effective
    )
