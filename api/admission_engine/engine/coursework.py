from collections import defaultdict
from typing import Literal

from api.admission_engine.engine.academic import rigor_score
from api.admission_engine.schemas.academic import RigorEvidence
from api.admission_engine.schemas.coursework import (
    CourseworkComponent,
    CourseworkComponentKey,
    CourseworkConfidence,
    CourseworkEvaluationRequest,
    CourseworkEvaluationResponse,
    CourseworkRating,
)

CORE_AREAS = {"ENGLISH", "MATHEMATICS", "LAB_SCIENCE", "SOCIAL_SCIENCE", "FOREIGN_LANGUAGE"}
ADVANCED_LEVELS = {"HONORS", "AP", "IB_SL", "IB_HL", "A_LEVEL", "DUAL_ENROLLMENT", "OTHER_ADVANCED"}
LEVEL_RANK = {"STANDARD": 0, "HONORS": 1, "IB_SL": 1, "OTHER_ADVANCED": 1, "AP": 2, "IB_HL": 2, "A_LEVEL": 2, "DUAL_ENROLLMENT": 2}


def _progression(
    payload: CourseworkEvaluationRequest,
) -> Literal["INCREASING", "STABLE", "MIXED", "DECLINING"]:
    by_grade: dict[int, list[int]] = defaultdict(list)
    for course in payload.courses:
        by_grade[course.grade_level].append(LEVEL_RANK[course.course_level])
    averages = [sum(by_grade[grade]) / len(by_grade[grade]) for grade in sorted(by_grade)]
    if len(averages) < 2 or len(set(averages)) == 1:
        return "STABLE"
    changes = [right - left for left, right in zip(averages, averages[1:], strict=False)]
    if all(change >= 0 for change in changes):
        return "INCREASING"
    if averages[-1] < averages[0]:
        return "DECLINING"
    return "MIXED"


def evaluate_coursework(payload: CourseworkEvaluationRequest) -> CourseworkEvaluationResponse:
    represented = {course.subject_area for course in payload.courses if course.subject_area in CORE_AREAS}
    highest = {
        area for area in represented
        if area in payload.highest_levels_available
        and any(course.subject_area == area and course.course_level == payload.highest_levels_available[area] for course in payload.courses)
    }
    coverage_count = len(represented)
    coverage: Literal["ALL", "MINOR_GAP", "MAJOR_GAP", "MULTIPLE_GAPS"] = "ALL" if coverage_count == 5 else "MINOR_GAP" if coverage_count == 4 else "MAJOR_GAP" if coverage_count == 3 else "MULTIPLE_GAPS"
    advanced_taken = sum(course.course_level in ADVANCED_LEVELS for course in payload.courses)
    progression = _progression(payload)
    major_courses = [course for course in payload.courses if course.is_major_related]
    advanced_major = sum(course.course_level in ADVANCED_LEVELS for course in major_courses)
    major: Literal["STRONG", "ADEQUATE", "LIMITED", "MISSING"] = "STRONG" if len(major_courses) >= 3 and advanced_major >= 1 else "ADEQUATE" if len(major_courses) >= 2 else "LIMITED" if major_courses else "MISSING"
    raw = rigor_score(RigorEvidence(
        highest_level_core_areas=len(highest), relevant_core_areas=len(represented),
        core_coverage=coverage, advanced_taken=advanced_taken,
        advanced_opportunities=payload.advanced_courses_available,
        progression=progression, major_preparation=major,
    ))
    assert raw is not None
    no_penalty = payload.advanced_courses_available == 0
    context = payload.school_context_notes or (
        "No advanced courses are available at the school." if no_penalty
        else f"School reports {payload.advanced_courses_available} advanced course opportunities across {', '.join(payload.advanced_program_types) or 'unspecified programs'}."
    )
    definitions: list[tuple[CourseworkComponentKey, str, int, int, str, str, str]] = [
        ("challenge", "Challenge level", raw.challenge, 40, f"Highest available level taken in {len(highest)} of {len(represented)} represented core areas.", "Rigor §6.1", "Compares selected courses with the highest levels explicitly reported for this school."),
        ("core_coverage", "Core coverage", raw.core_coverage, 20, f"Courses cover {coverage_count} of 5 canonical core areas.", "Rigor §6.2", "Checks English, mathematics, laboratory science, social science, and foreign language coverage."),
        ("advanced_utilization", "Advanced utilization", raw.advanced_utilization, 20, "No advanced opportunities available; neutral context score applied." if no_penalty else f"{advanced_taken} of {payload.advanced_courses_available} reported advanced opportunities used.", "ACAD-005" if no_penalty else "Rigor §6.3", "No penalty is applied when the school reports zero advanced opportunities." if no_penalty else "Uses advanced courses taken as a share of opportunities explicitly reported by the school."),
        ("progression", "Progression", raw.progression, 10, f"Course-level pattern across grades {', '.join(map(str, sorted(set(payload.grade_levels))))}: {progression.lower()}.", "Rigor §6.4", "Compares average documented course-level challenge from one grade level to the next."),
        ("major_preparation", "Major preparation", raw.major_preparation, 10, f"{len(major_courses)} course(s) marked relevant to {payload.intended_major}; {advanced_major} advanced.", "Rigor §6.5", "Uses only courses explicitly marked as related to the intended major."),
    ]
    components = [CourseworkComponent(key=key, label=label, score=None if no_penalty and key == "advanced_utilization" else round(points / maximum * 100, 1), points=points, points_available=maximum, evidence=evidence, rule=rule, explanation=explanation) for key, label, points, maximum, evidence, rule, explanation in definitions]
    confidence: CourseworkConfidence = "HIGH" if represented and represented.issubset(payload.highest_levels_available) and payload.school_context_notes else "MEDIUM" if payload.highest_levels_available else "LOW"
    rating: CourseworkRating = "STRONG" if raw.total >= 85 else "SOLID" if raw.total >= 70 else "MODERATE" if raw.total >= 55 else "LIMITED"
    rules = [{"rule_id": "ACAD-005", "severity": "INFO", "message": "No advanced courses available; no penalty applied."}] if no_penalty else []
    return CourseworkEvaluationResponse(overall_score=float(raw.total), display_score=raw.total, rating=rating, confidence=confidence, components=components, school_context=context, no_advanced_penalty=no_penalty, formula="Challenge (40) + Core coverage (20) + Advanced utilization (20) + Progression (10) + Major preparation (10)", triggered_rules=rules)
