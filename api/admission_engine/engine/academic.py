from statistics import fmean

from api.admission_engine.engine.scoring import clamp, weighted_score
from api.admission_engine.schemas.academic import (
    AcademicEvaluationRequest,
    AcademicEvaluationResponse,
    AcademicScores,
    RigorEvidence,
    RigorScores,
)

ACADEMIC_WEIGHTS = {
    "performance": 0.45,
    "rigor": 0.30,
    "trend": 0.10,
    "context": 0.10,
    "major_preparation": 0.05,
}


def _interpolate(x: float, left_x: float, left_y: float, right_x: float, right_y: float) -> float:
    if right_x == left_x:
        return left_y
    ratio = (x - left_x) / (right_x - left_x)
    return left_y + ratio * (right_y - left_y)


def performance_score(request: AcademicEvaluationRequest) -> float | None:
    averages = [term.average_grade for term in request.terms if term.average_grade is not None]
    if not averages or request.scale_min is None or request.scale_max is None:
        return None
    average = fmean(float(value) for value in averages)
    normalized = (average - request.scale_min) / (request.scale_max - request.scale_min)
    anchors = [
        (0.0, 20.0),
        (0.60, 58.0),
        (0.65, 64.0),
        (0.70, 70.0),
        (0.75, 76.0),
        (0.80, 82.0),
        (0.85, 88.0),
        (0.90, 94.0),
        (0.95, 100.0),
    ]
    if normalized <= anchors[0][0]:
        base = anchors[0][1]
    elif normalized >= anchors[-1][0]:
        base = anchors[-1][1]
    else:
        base = next(
            _interpolate(normalized, left_x, left_y, right_x, right_y)
            for (left_x, left_y), (right_x, right_y) in zip(anchors, anchors[1:], strict=True)
            if left_x <= normalized < right_x
        )

    if request.class_rank is not None and request.class_size is not None:
        percentile = request.class_rank / request.class_size
        base += (
            6
            if percentile <= 0.01
            else 5
            if percentile <= 0.05
            else 4
            if percentile <= 0.10
            else 2
            if percentile <= 0.20
            else 1
            if percentile <= 0.30
            else 0
        )

    major_grades = [
        float(course.grade_value)
        for course in request.courses
        if course.is_major_related and course.grade_value is not None
    ]
    if len(major_grades) >= 3:
        difference = fmean(major_grades) - average
        base += 3 if difference >= 3 else 1 if difference >= 1 else -3 if difference <= -3 else 0
    return round(clamp(base), 2)


def trend_score(request: AcademicEvaluationRequest) -> tuple[float | None, float | None]:
    values = [
        float(term.average_grade)
        for term in sorted(request.terms, key=lambda item: item.term_order)
        if term.average_grade is not None
    ]
    if len(values) < 2:
        return None, None
    xs = list(range(len(values)))
    x_mean, y_mean = fmean(xs), fmean(values)
    denominator = sum((x - x_mean) ** 2 for x in xs)
    slope = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, values, strict=True)) / denominator
    score = (
        100
        if slope >= 2
        else 90
        if slope >= 1
        else 82
        if slope >= 0.5
        else 75
        if slope >= -0.49
        else 65
        if slope >= -0.99
        else 50
        if slope >= -1.99
        else 35
    )
    return float(score), round(slope, 4)


def rigor_score(evidence: RigorEvidence | None) -> RigorScores | None:
    if evidence is None:
        return None
    if evidence.relevant_core_areas == 0:
        challenge = 40
    else:
        ratio = evidence.highest_level_core_areas / evidence.relevant_core_areas
        challenge = (
            40
            if ratio >= 0.8
            else 34
            if ratio >= 0.6
            else 27
            if ratio >= 0.4
            else 20
            if ratio >= 0.2
            else 12
        )

    coverage = {"ALL": 20, "MINOR_GAP": 16, "MAJOR_GAP": 11, "MULTIPLE_GAPS": 5}[
        evidence.core_coverage
    ]
    if evidence.advanced_opportunities == 0:
        advanced = 16
    else:
        ratio = evidence.advanced_taken / evidence.advanced_opportunities
        advanced = (
            20
            if ratio >= 0.8
            else 17
            if ratio >= 0.6
            else 13
            if ratio >= 0.4
            else 9
            if ratio >= 0.2
            else 5
            if ratio > 0
            else 2
        )
    progression = {"INCREASING": 10, "STABLE": 8, "MIXED": 6, "DECLINING": 3}[evidence.progression]
    major = {"STRONG": 10, "ADEQUATE": 7, "LIMITED": 4, "MISSING": 1}[evidence.major_preparation]
    return RigorScores(
        challenge=challenge,
        core_coverage=coverage,
        advanced_utilization=advanced,
        progression=progression,
        major_preparation=major,
        total=challenge + coverage + advanced + progression + major,
    )


def evaluate_academic(request: AcademicEvaluationRequest) -> AcademicEvaluationResponse:
    performance = performance_score(request)
    trend, slope = trend_score(request)
    rigor = rigor_score(request.rigor_evidence)
    major_preparation = float(rigor.major_preparation * 10) if rigor else None
    scores = AcademicScores(
        performance=performance,
        rigor=float(rigor.total) if rigor else None,
        trend=trend,
        context=request.academic_context_score,
        major_preparation=major_preparation,
    )
    overall = weighted_score(scores.model_dump(), ACADEMIC_WEIGHTS)
    return AcademicEvaluationResponse(
        overall_score=overall,
        display_score=round(overall) if overall is not None else None,
        components=scores,
        rigor_details=rigor,
        trend_slope=slope,
    )
