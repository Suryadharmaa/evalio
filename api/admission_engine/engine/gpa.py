from api.admission_engine.schemas.gpa import (
    CourseLevel,
    GpaCalculationRequest,
    GpaCalculationResponse,
    GpaCourseResult,
)

GRADE_POINTS = {
    "A+": 4.0, "A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "C-": 1.7, "D+": 1.3, "D": 1.0, "D-": 0.7, "F": 0.0,
}
PRESET_OFFSETS: dict[CourseLevel, float] = {
    "REGULAR": 0.0, "HONORS": 0.5, "AP": 1.0, "IB": 1.0,
    "DUAL_ENROLLMENT": 1.0, "OTHER_ADVANCED": 1.0,
}


def _rounded(value: float) -> float:
    return round(value + 1e-12, 3)


def calculate_gpa(payload: GpaCalculationRequest) -> GpaCalculationResponse:
    if payload.mode == "INTERNATIONAL_RAW":
        total_weight = sum(item.weight for item in payload.international_grades)
        average = sum(item.value * item.weight for item in payload.international_grades) / total_weight
        return GpaCalculationResponse(
            mode=payload.mode,
            academic_average=_rounded(average), scale_min=payload.scale_min,
            scale_max=payload.scale_max, total_credits_or_weight=_rounded(total_weight),
            conversion="NOT_APPLIED",
            formula=["Academic average = sum(grade × weight) ÷ sum(weight)", "No conversion to a 4.0 scale is applied."],
            breakdown=[GpaCourseResult(label=item.label, credits_or_weight=item.weight, base_value=item.value) for item in payload.international_grades],
        )

    total_credits = sum(course.credits for course in payload.courses)
    offsets: dict[CourseLevel, float]
    if payload.weighting_method == "NONE":
        offsets = {level: 0.0 for level in PRESET_OFFSETS}
    elif payload.weighting_method == "CUSTOM":
        offsets = {level: (payload.custom_offsets or {}).get(level, 0.0) for level in PRESET_OFFSETS}
    else:
        offsets = PRESET_OFFSETS
    breakdown = []
    unweighted_total = weighted_total = 0.0
    for course in payload.courses:
        base = GRADE_POINTS[course.grade]
        weighted = base + offsets[course.course_level]
        unweighted_total += base * course.credits
        weighted_total += weighted * course.credits
        breakdown.append(GpaCourseResult(label=course.course, credits_or_weight=course.credits, base_value=base, weighted_value=weighted, course_level=course.course_level))
    return GpaCalculationResponse(
        mode=payload.mode, unweighted_gpa=_rounded(unweighted_total / total_credits),
        weighted_gpa=_rounded(weighted_total / total_credits), total_credits_or_weight=_rounded(total_credits),
        conversion="NOT_APPLIED", weighting_method=payload.weighting_method,
        formula=["Unweighted GPA = sum(standard letter-grade points × credits) ÷ sum(credits)", "Weighted GPA = sum((grade points + selected course-level offset) × credits) ÷ sum(credits)"],
        breakdown=breakdown,
    )
