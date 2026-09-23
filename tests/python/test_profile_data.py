from api.admission_engine.database.models import Activity, Course, SchoolContext
from api.admission_engine.routers.profile_data import (
    activity_input_from_saved,
    rigor_from_saved_courses,
)


def test_saved_course_rigor_uses_explicit_school_opportunities() -> None:
    courses = [
        Course(
            course_name=f"Course {index}",
            subject_area=subject,
            is_advanced=index < 3,
            is_highest_available=index < 4,
            is_major_related=index < 2,
        )
        for index, subject in enumerate(["Math", "Science", "English", "Social", "Language"])
    ]
    context = SchoolContext(advanced_courses_available=6)

    result = rigor_from_saved_courses(courses, context)

    assert result is not None
    assert result.core_coverage == "ALL"
    assert result.highest_level_core_areas == 4
    assert result.advanced_taken == 3
    assert result.advanced_opportunities == 6
    assert result.major_preparation == "ADEQUATE"


def test_saved_course_rigor_requires_school_opportunity_context() -> None:
    courses = [Course(course_name="Calculus", subject_area="Math", is_advanced=True)]

    assert rigor_from_saved_courses(courses, None) is None


def test_non_core_course_labels_do_not_inflate_rigor_coverage() -> None:
    courses = [
        Course(course_name=name, subject_area=name, is_highest_available=True)
        for name in ("Art", "Physical Education", "Music", "Theater", "Design")
    ]

    assert rigor_from_saved_courses(courses, SchoolContext(advanced_courses_available=3)) is None


def test_founder_title_alone_does_not_become_responsibility_evidence() -> None:
    title_only = activity_input_from_saved(
        Activity(
            activity_name="Club",
            is_founder=True,
            description="Member of a club",
            duration_months=24,
        )
    )
    evidenced = activity_input_from_saved(
        Activity(
            activity_name="Club",
            is_founder=True,
            description="Created and managed weekly workshops",
            duration_months=24,
        )
    )

    assert not title_only.founder_responsibility_evidence
    assert title_only.initiative_level == "STARTED_PROJECT"
    assert evidenced.founder_responsibility_evidence
    assert evidenced.sustained_operations
