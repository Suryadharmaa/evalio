import hashlib
import json
import uuid
from datetime import UTC, date, datetime, time
from decimal import Decimal
from typing import Any, cast

from fastapi import APIRouter, Depends, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.admission_engine.application.dependencies import (
    CurrentUserDependency,
    SessionDependency,
    get_identity,
)
from api.admission_engine.config import ENGINE_VERSION
from api.admission_engine.database.models import (
    AcademicTerm,
    Activity,
    ApplicantProfile,
    ApplicationMaterialStatus,
    College,
    CollegeAdmissions,
    CollegeCdsFactor,
    CollegeFinancialAid,
    CollegeRequirement,
    CollegeSource,
    Course,
    Essay,
    EssayMetric,
    Evaluation,
    EvaluationComponent,
    Honor,
    Recommendation,
    SchoolContext,
    TargetCollege,
    TestScore,
    TriggeredRule,
)
from api.admission_engine.engine.academic import evaluate_academic
from api.admission_engine.engine.activities import evaluate_activities, evaluate_activity
from api.admission_engine.engine.college import (
    audit_application,
    evaluate_college,
    evaluate_financial,
)
from api.admission_engine.engine.essay import evaluate_essay
from api.admission_engine.engine.honors import evaluate_honor
from api.admission_engine.engine.lor import evaluate_lor
from api.admission_engine.errors import DomainError, NotFoundError
from api.admission_engine.schemas.academic import (
    AcademicEvaluationRequest,
    AcademicEvaluationResponse,
    AcademicTermInput,
    CourseInput,
    RigorEvidence,
)
from api.admission_engine.schemas.activities import ActivityEvaluationRequest, ActivityInput
from api.admission_engine.schemas.college_evaluation import (
    ApplicationAuditRequest,
    CollegeEvaluationRequest,
    FinancialEvaluationRequest,
    MaterialStatus,
    PublishedRange,
)
from api.admission_engine.schemas.common import ApiModel
from api.admission_engine.schemas.essay import (
    EssayEvaluationRequest,
    SavedEssayCreate,
    SavedEssayHistoryItem,
    SavedEssayRead,
)
from api.admission_engine.schemas.honors import HonorInput
from api.admission_engine.schemas.lor import (
    LorEvaluationRequest,
    SavedRecommendationCreate,
    SavedRecommendationRead,
)
from api.admission_engine.schemas.profile_data import (
    AcademicTermRead,
    AcademicTermWrite,
    ActivityPatch,
    ActivityRead,
    ActivityWrite,
    CourseRead,
    CourseWrite,
    EvaluationRead,
    HonorPatch,
    HonorRead,
    HonorWrite,
    MaterialStatusRead,
    MaterialStatusWrite,
    SchoolContextRead,
    SchoolContextWrite,
    TargetPatch,
    TargetRead,
    TargetWithCollege,
    TargetWrite,
    TestScorePatch,
    TestScoreRead,
    TestScoreWrite,
)

router = APIRouter(
    prefix="/api/v1/profiles", tags=["profile data"], dependencies=[Depends(get_identity)]
)


class EvaluationDate(ApiModel):
    evaluation_date: date = Field(default_factory=date.today)


def normalized_triggered_rules(
    data: dict[str, Any], *, evaluation_type: str, confidence: str
) -> list[dict[str, object]]:
    """Preserve structured rule evidence while supporting legacy rule-id lists."""
    records: list[dict[str, object]] = []
    seen: set[str] = set()

    def add(value: object, *, fallback_message: str) -> None:
        if isinstance(value, str):
            rule_id = value
            payload: dict[str, object] = {}
        elif isinstance(value, dict):
            payload = value
            candidate = payload.get("rule_id")
            if not isinstance(candidate, str):
                return
            rule_id = candidate
        else:
            return
        if not rule_id or rule_id in seen:
            return
        seen.add(rule_id)
        evidence = payload.get("evidence", {})
        records.append(
            {
                "rule_id": rule_id,
                "rule_version": str(payload.get("rule_version", "1.0.0")),
                "severity": str(payload.get("severity", "INFO")),
                "category": str(payload.get("category", evaluation_type)),
                "message": str(payload.get("message", payload.get("title", fallback_message))),
                "score_delta": payload.get("score_delta"),
                "confidence": str(payload.get("confidence", confidence)),
                "evidence": evidence if isinstance(evidence, dict) else {},
            }
        )

    issues = data.get("issues", [])
    if isinstance(issues, list):
        for issue in issues:
            add(issue, fallback_message="Deterministic issue detected.")
    triggered = data.get("triggered_rules", [])
    if isinstance(triggered, list):
        for rule in triggered:
            add(rule, fallback_message="Deterministic rule triggered.")
    return records


async def persist_evaluation(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    profile_id: uuid.UUID,
    evaluation_type: str,
    input_data: object,
    result: BaseModel,
    subject_entity_id: uuid.UUID | None = None,
    college_id: uuid.UUID | None = None,
    evaluation_date: date | None = None,
) -> Evaluation:
    data = result.model_dump(mode="json")
    serialized = json.dumps(input_data, sort_keys=True, separators=(",", ":"), default=str)
    overall = data.get(
        "overall_score",
        data.get(
            "portfolio_score",
            data.get("completeness_score", data.get("application_strength")),
        ),
    )
    display_score = data.get("display_score")
    if not isinstance(display_score, int) and isinstance(overall, (int, float)):
        display_score = round(overall)
    row = Evaluation(
        user_id=user_id,
        profile_id=profile_id,
        evaluation_type=evaluation_type,
        subject_entity_id=subject_entity_id,
        college_id=college_id,
        engine_version=str(data.get("engine_version", ENGINE_VERSION)),
        rubric_version=str(data.get("rubric_version", f"{evaluation_type.casefold()}-1.0.0")),
        overall_score=overall if isinstance(overall, (int, float)) else None,
        display_score=display_score if isinstance(display_score, int) else None,
        confidence=str(data.get("confidence", "LOW")),
        status=(
            "INCOMPLETE"
            if data.get("readiness") in {"INCOMPLETE", "DEADLINE_PASSED"}
            else "COMPLETE"
            if overall is not None
            else "INCOMPLETE"
        ),
        input_hash=hashlib.sha256(serialized.encode()).hexdigest(),
        evaluation_date=evaluation_date or date.today(),
    )
    session.add(row)
    await session.flush()
    components = data.get("components")
    if isinstance(components, dict):
        for name, value in components.items():
            if isinstance(value, (int, float)):
                session.add(
                    EvaluationComponent(
                        evaluation_id=row.id, component_name=name, score=value, status="COMPLETE"
                    )
                )
    metrics = data.get("metrics")
    if evaluation_type == "ESSAY" and subject_entity_id is not None and isinstance(metrics, dict):
        word_count = int(metrics.get("word_count", 0))
        paragraph_count = int(metrics.get("paragraph_count", 0))
        session.add(
            EssayMetric(
                essay_id=subject_entity_id,
                word_count=word_count,
                character_count=int(metrics.get("character_count", 0)),
                sentence_count=int(metrics.get("sentence_count", 0)),
                paragraph_count=paragraph_count,
                avg_sentence_length=metrics.get("average_sentence_length", 0),
                median_sentence_length=metrics.get("median_sentence_length", 0),
                sentence_length_stddev=metrics.get("sentence_length_stddev", 0),
                avg_paragraph_length=(
                    round(word_count / paragraph_count, 3) if paragraph_count else None
                ),
                flesch_reading_ease=metrics.get("flesch_reading_ease"),
                flesch_kincaid_grade=None,
                lexical_diversity=metrics.get("lexical_diversity"),
                reflection_density=metrics.get("reflection_density"),
                specificity_density=metrics.get("specificity_density"),
                repetition_rate=None,
                metrics_version=str(data.get("rubric_version", "essay-1.0.0")),
            )
        )
    for rule in normalized_triggered_rules(
        data, evaluation_type=evaluation_type, confidence=row.confidence
    ):
        session.add(TriggeredRule(evaluation_id=row.id, **rule))
    await session.flush()
    return row


def envelope(request: Request, data: object) -> dict[str, object]:
    return {
        "data": data,
        "meta": {"request_id": request.state.request_id, "engine_version": ENGINE_VERSION},
    }


async def owned_profile(
    session: AsyncSession, profile_id: uuid.UUID, user_id: uuid.UUID
) -> ApplicantProfile:
    profile = await session.scalar(
        select(ApplicantProfile).where(
            ApplicantProfile.id == profile_id, ApplicantProfile.user_id == user_id
        )
    )
    if profile is None:
        raise NotFoundError("Profile not found")
    return profile


async def owned_child[ModelT](
    session: AsyncSession, model: type[ModelT], item_id: uuid.UUID, profile_id: uuid.UUID
) -> ModelT:
    item = await session.scalar(
        select(model).where(model.id == item_id, model.profile_id == profile_id)  # type: ignore[attr-defined]
    )
    if item is None:
        raise NotFoundError("Item not found")
    return item


def activity_input_from_saved(row: Activity) -> ActivityInput:
    leadership = {"PARTICIPANT", "INFORMAL", "OPERATIONAL", "LEAD", "EXECUTIVE", "FOUNDER"}
    recognition = {"NONE", "SCHOOL_LOCAL", "REGIONAL", "STATE", "NATIONAL", "INTERNATIONAL"}
    progression = ("NONE", "SOME", "CLEAR", "MULTIPLE")
    description = (row.description or "").casefold()
    responsibility_evidence = bool(
        row.is_founder
        and any(
            marker in description
            for marker in ("built", "created", "launched", "managed", "led", "organized")
        )
    )
    return ActivityInput(
        activity_name=row.activity_name,
        people_impacted=row.people_impacted,
        impact_level="SMALL_GROUP" if (row.people_impacted or 0) > 0 else "NONE",
        leadership_level=cast(Any, row.leadership_level)
        if row.leadership_level in leadership
        else ("FOUNDER" if row.is_founder else "PARTICIPANT"),
        founder_responsibility_evidence=responsibility_evidence,
        sustained_operations=responsibility_evidence and (row.duration_months or 0) >= 12,
        duration_months=row.duration_months or 0,
        initiative_level="CREATED_PROGRAM"
        if responsibility_evidence
        else "STARTED_PROJECT"
        if row.is_founder
        else "ASSIGNED",
        hours_per_week=float(row.hours_per_week or 0),
        recognition_scope=cast(Any, row.recognition_scope)
        if row.recognition_scope in recognition
        else "NONE",
        progression_level=cast(Any, progression[min(max(row.progression_level or 0, 0), 3)]),
    )


def honor_input_from_saved(row: Honor, intended_major: str | None) -> HonorInput:
    valid_scopes = {"SCHOOL", "LOCAL", "REGIONAL", "STATE", "NATIONAL", "INTERNATIONAL"}
    valid_placements = {
        "PARTICIPANT",
        "HONORABLE_MENTION",
        "TOP_10",
        "TOP_5",
        "THIRD",
        "SECOND",
        "FIRST",
    }
    return HonorInput(
        honor_name=row.honor_name,
        scope=cast(Any, row.scope if row.scope in valid_scopes else None),
        selection_rate=float(row.selection_rate) if row.selection_rate is not None else None,
        placement=cast(Any, row.placement if row.placement in valid_placements else "PARTICIPANT"),
        academic_relevance=(
            15
            if row.academic_area
            and intended_major
            and (
                row.academic_area.casefold() in intended_major.casefold()
                or intended_major.casefold() in row.academic_area.casefold()
            )
            else 8
            if row.academic_area
            else 0
        ),
        repeat_count=row.repeat_count,
        organizer=row.organizer,
        countries_represented=row.countries_represented,
    )


def apply_patch(item: object, values: dict[str, Any]) -> None:
    for key, value in values.items():
        setattr(item, key, value)


def rigor_from_saved_courses(
    courses: list[Course], school_context: SchoolContext | None
) -> RigorEvidence | None:
    if school_context is None or school_context.advanced_courses_available is None:
        return None

    def core_area(value: str | None) -> str | None:
        normalized = (value or "").strip().casefold()
        groups = {
            "english": ("english", "literature", "writing"),
            "math": ("math", "algebra", "geometry", "calculus", "statistics"),
            "science": ("science", "biology", "chemistry", "physics", "laboratory"),
            "social_science": (
                "social",
                "history",
                "geography",
                "economics",
                "civics",
                "government",
            ),
            "foreign_language": (
                "language",
                "spanish",
                "french",
                "german",
                "mandarin",
                "chinese",
                "japanese",
                "latin",
                "arabic",
            ),
        }
        return next(
            (
                group
                for group, markers in groups.items()
                if any(marker in normalized for marker in markers)
            ),
            None,
        )

    subject_areas = {area for row in courses if (area := core_area(row.subject_area)) is not None}
    if not subject_areas:
        return None
    highest_areas = {
        area
        for row in courses
        if row.is_highest_available and (area := core_area(row.subject_area)) is not None
    }
    relevant = min(len(subject_areas), 5)
    highest = min(len(highest_areas), relevant)
    coverage = (
        "ALL"
        if relevant >= 5
        else "MINOR_GAP"
        if relevant == 4
        else "MAJOR_GAP"
        if relevant == 3
        else "MULTIPLE_GAPS"
    )
    advanced_taken = sum(bool(row.is_advanced) for row in courses)
    opportunities = max(school_context.advanced_courses_available, advanced_taken)
    major_courses = sum(bool(row.is_major_related) for row in courses)
    major_preparation = (
        "STRONG"
        if major_courses >= 3
        else "ADEQUATE"
        if major_courses == 2
        else "LIMITED"
        if major_courses == 1
        else "MISSING"
    )
    return RigorEvidence(
        highest_level_core_areas=highest,
        relevant_core_areas=relevant,
        core_coverage=cast(Any, coverage),
        advanced_taken=advanced_taken,
        advanced_opportunities=opportunities,
        progression="MIXED",
        major_preparation=cast(Any, major_preparation),
    )


@router.put("/{profile_id}/academic-terms")
async def replace_academic_terms(
    profile_id: uuid.UUID,
    payload: list[AcademicTermWrite],
    request: Request,
    session: SessionDependency,
    user: CurrentUserDependency,
) -> dict[str, object]:
    await owned_profile(session, profile_id, user.id)
    if len(payload) > 30:
        raise DomainError("A profile may contain at most 30 academic terms", code="LIMIT_EXCEEDED")
    await session.execute(delete(AcademicTerm).where(AcademicTerm.profile_id == profile_id))
    rows = [AcademicTerm(profile_id=profile_id, **item.model_dump()) for item in payload]
    session.add_all(rows)
    await session.commit()
    for row in rows:
        await session.refresh(row)
    return envelope(request, [AcademicTermRead.model_validate(row) for row in rows])


@router.get("/{profile_id}/academic-terms")
async def list_academic_terms(
    profile_id: uuid.UUID,
    request: Request,
    session: SessionDependency,
    user: CurrentUserDependency,
) -> dict[str, object]:
    await owned_profile(session, profile_id, user.id)
    rows = list(
        await session.scalars(
            select(AcademicTerm)
            .where(AcademicTerm.profile_id == profile_id)
            .order_by(AcademicTerm.term_order)
        )
    )
    return envelope(request, [AcademicTermRead.model_validate(row) for row in rows])


@router.put("/{profile_id}/courses")
async def replace_courses(
    profile_id: uuid.UUID,
    payload: list[CourseWrite],
    request: Request,
    session: SessionDependency,
    user: CurrentUserDependency,
) -> dict[str, object]:
    await owned_profile(session, profile_id, user.id)
    if len(payload) > 200:
        raise DomainError("A profile may contain at most 200 courses", code="LIMIT_EXCEEDED")
    term_ids = {item.term_id for item in payload if item.term_id is not None}
    if term_ids:
        valid_ids = set(
            await session.scalars(
                select(AcademicTerm.id).where(
                    AcademicTerm.profile_id == profile_id, AcademicTerm.id.in_(term_ids)
                )
            )
        )
        if valid_ids != term_ids:
            raise NotFoundError("One or more academic terms were not found")
    await session.execute(delete(Course).where(Course.profile_id == profile_id))
    rows = [Course(profile_id=profile_id, **item.model_dump()) for item in payload]
    session.add_all(rows)
    await session.commit()
    return envelope(request, [CourseRead.model_validate(row) for row in rows])


@router.get("/{profile_id}/courses")
async def list_courses(
    profile_id: uuid.UUID,
    request: Request,
    session: SessionDependency,
    user: CurrentUserDependency,
) -> dict[str, object]:
    await owned_profile(session, profile_id, user.id)
    rows = list(
        await session.scalars(
            select(Course).where(Course.profile_id == profile_id).order_by(Course.course_name)
        )
    )
    return envelope(request, [CourseRead.model_validate(row) for row in rows])


@router.get("/{profile_id}/school-context")
async def get_school_context(
    profile_id: uuid.UUID,
    request: Request,
    session: SessionDependency,
    user: CurrentUserDependency,
) -> dict[str, object]:
    await owned_profile(session, profile_id, user.id)
    row = await session.scalar(select(SchoolContext).where(SchoolContext.profile_id == profile_id))
    return envelope(request, SchoolContextRead.model_validate(row) if row else None)


@router.put("/{profile_id}/school-context")
async def put_school_context(
    profile_id: uuid.UUID,
    payload: SchoolContextWrite,
    request: Request,
    session: SessionDependency,
    user: CurrentUserDependency,
) -> dict[str, object]:
    await owned_profile(session, profile_id, user.id)
    row = await session.scalar(select(SchoolContext).where(SchoolContext.profile_id == profile_id))
    if row is None:
        row = SchoolContext(profile_id=profile_id, **payload.model_dump())
        session.add(row)
    else:
        apply_patch(row, payload.model_dump())
    await session.commit()
    await session.refresh(row)
    return envelope(request, SchoolContextRead.model_validate(row))


@router.post("/{profile_id}/evaluate/academic")
async def evaluate_saved_academic(
    profile_id: uuid.UUID,
    request: Request,
    session: SessionDependency,
    user: CurrentUserDependency,
) -> dict[str, object]:
    profile = await owned_profile(session, profile_id, user.id)
    terms = list(
        await session.scalars(
            select(AcademicTerm)
            .where(AcademicTerm.profile_id == profile_id)
            .order_by(AcademicTerm.term_order)
        )
    )
    if not terms:
        raise NotFoundError("Add academic terms before evaluating")
    courses = list(await session.scalars(select(Course).where(Course.profile_id == profile_id)))
    school_context = await session.scalar(
        select(SchoolContext).where(SchoolContext.profile_id == profile_id)
    )
    payload = AcademicEvaluationRequest(
        terms=[
            AcademicTermInput(term_order=row.term_order, average_grade=row.average_grade)
            for row in terms
        ],
        courses=[
            CourseInput(grade_value=row.grade_value, is_major_related=bool(row.is_major_related))
            for row in courses
        ],
        scale_min=float(profile.grading_scale_min)
        if profile.grading_scale_min is not None
        else None,
        scale_max=float(profile.grading_scale_max)
        if profile.grading_scale_max is not None
        else None,
        class_rank=profile.class_rank,
        class_size=profile.class_size,
        rigor_evidence=rigor_from_saved_courses(courses, school_context),
    )
    result = evaluate_academic(payload)
    await persist_evaluation(
        session,
        user_id=user.id,
        profile_id=profile_id,
        evaluation_type="ACADEMIC",
        input_data=payload.model_dump(mode="json"),
        result=result,
    )
    await session.commit()
    return envelope(request, {"evaluation": result})


@router.get("/{profile_id}/tests")
async def list_tests(
    profile_id: uuid.UUID, request: Request, session: SessionDependency, user: CurrentUserDependency
) -> dict[str, object]:
    await owned_profile(session, profile_id, user.id)
    rows = list(await session.scalars(select(TestScore).where(TestScore.profile_id == profile_id)))
    return envelope(request, [TestScoreRead.model_validate(row) for row in rows])


@router.post("/{profile_id}/tests", status_code=status.HTTP_201_CREATED)
async def create_test(
    profile_id: uuid.UUID,
    payload: TestScoreWrite,
    request: Request,
    session: SessionDependency,
    user: CurrentUserDependency,
) -> dict[str, object]:
    await owned_profile(session, profile_id, user.id)
    row = TestScore(profile_id=profile_id, **payload.model_dump())
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return envelope(request, TestScoreRead.model_validate(row))


@router.patch("/{profile_id}/tests/{item_id}")
async def update_test(
    profile_id: uuid.UUID,
    item_id: uuid.UUID,
    payload: TestScorePatch,
    request: Request,
    session: SessionDependency,
    user: CurrentUserDependency,
) -> dict[str, object]:
    await owned_profile(session, profile_id, user.id)
    row = await owned_child(session, TestScore, item_id, profile_id)
    apply_patch(row, payload.model_dump(exclude_unset=True))
    await session.commit()
    await session.refresh(row)
    return envelope(request, TestScoreRead.model_validate(row))


@router.delete("/{profile_id}/tests/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_test(
    profile_id: uuid.UUID,
    item_id: uuid.UUID,
    session: SessionDependency,
    user: CurrentUserDependency,
) -> None:
    await owned_profile(session, profile_id, user.id)
    await session.delete(await owned_child(session, TestScore, item_id, profile_id))
    await session.commit()


@router.get("/{profile_id}/activities")
async def list_activities(
    profile_id: uuid.UUID, request: Request, session: SessionDependency, user: CurrentUserDependency
) -> dict[str, object]:
    await owned_profile(session, profile_id, user.id)
    rows = list(
        await session.scalars(
            select(Activity)
            .where(Activity.profile_id == profile_id)
            .order_by(Activity.activity_order, Activity.id)
        )
    )
    return envelope(
        request,
        [
            ActivityRead.model_validate(row).model_copy(
                update={"current_score": evaluate_activity(activity_input_from_saved(row)).total}
            )
            for row in rows
        ],
    )


@router.post("/{profile_id}/activities", status_code=status.HTTP_201_CREATED)
async def create_activity(
    profile_id: uuid.UUID,
    payload: ActivityWrite,
    request: Request,
    session: SessionDependency,
    user: CurrentUserDependency,
) -> dict[str, object]:
    await owned_profile(session, profile_id, user.id)
    count = await session.scalar(
        select(func.count()).select_from(Activity).where(Activity.profile_id == profile_id)
    )
    if (count or 0) >= 50:
        raise DomainError("A profile may contain at most 50 activities", code="LIMIT_EXCEEDED")
    row = Activity(profile_id=profile_id, **payload.model_dump())
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return envelope(request, ActivityRead.model_validate(row))


@router.patch("/{profile_id}/activities/{item_id}")
async def update_activity(
    profile_id: uuid.UUID,
    item_id: uuid.UUID,
    payload: ActivityPatch,
    request: Request,
    session: SessionDependency,
    user: CurrentUserDependency,
) -> dict[str, object]:
    await owned_profile(session, profile_id, user.id)
    row = await owned_child(session, Activity, item_id, profile_id)
    apply_patch(row, payload.model_dump(exclude_unset=True))
    await session.commit()
    await session.refresh(row)
    return envelope(request, ActivityRead.model_validate(row))


@router.delete("/{profile_id}/activities/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity(
    profile_id: uuid.UUID,
    item_id: uuid.UUID,
    session: SessionDependency,
    user: CurrentUserDependency,
) -> None:
    await owned_profile(session, profile_id, user.id)
    await session.delete(await owned_child(session, Activity, item_id, profile_id))
    await session.commit()


@router.post("/{profile_id}/evaluate/activities")
async def evaluate_saved_activities(
    profile_id: uuid.UUID, request: Request, session: SessionDependency, user: CurrentUserDependency
) -> dict[str, object]:
    await owned_profile(session, profile_id, user.id)
    rows = list(
        await session.scalars(
            select(Activity)
            .where(Activity.profile_id == profile_id)
            .order_by(Activity.activity_order, Activity.id)
        )
    )
    if not rows:
        raise NotFoundError("Add activities before evaluating")
    inputs = [activity_input_from_saved(row) for row in rows]
    payload = ActivityEvaluationRequest(activities=inputs)
    result = evaluate_activities(payload)
    await persist_evaluation(
        session,
        user_id=user.id,
        profile_id=profile_id,
        evaluation_type="ACTIVITY",
        input_data=payload.model_dump(mode="json"),
        result=result,
    )
    await session.commit()
    return envelope(request, {"evaluation": result})


@router.get("/{profile_id}/honors")
async def list_honors(
    profile_id: uuid.UUID, request: Request, session: SessionDependency, user: CurrentUserDependency
) -> dict[str, object]:
    profile = await owned_profile(session, profile_id, user.id)
    rows = list(await session.scalars(select(Honor).where(Honor.profile_id == profile_id)))
    return envelope(
        request,
        [
            HonorRead.model_validate(row).model_copy(
                update={
                    "current_score": evaluate_honor(
                        honor_input_from_saved(row, profile.intended_major)
                    ).display_score
                }
            )
            for row in rows
        ],
    )


@router.post("/{profile_id}/honors", status_code=status.HTTP_201_CREATED)
async def create_honor(
    profile_id: uuid.UUID,
    payload: HonorWrite,
    request: Request,
    session: SessionDependency,
    user: CurrentUserDependency,
) -> dict[str, object]:
    await owned_profile(session, profile_id, user.id)
    count = await session.scalar(
        select(func.count()).select_from(Honor).where(Honor.profile_id == profile_id)
    )
    if (count or 0) >= 50:
        raise DomainError("A profile may contain at most 50 honors", code="LIMIT_EXCEEDED")
    row = Honor(profile_id=profile_id, **payload.model_dump())
    session.add(row)
    await session.commit()
    return envelope(request, HonorRead.model_validate(row))


@router.patch("/{profile_id}/honors/{item_id}")
async def update_honor(
    profile_id: uuid.UUID,
    item_id: uuid.UUID,
    payload: HonorPatch,
    request: Request,
    session: SessionDependency,
    user: CurrentUserDependency,
) -> dict[str, object]:
    await owned_profile(session, profile_id, user.id)
    row = await owned_child(session, Honor, item_id, profile_id)
    apply_patch(row, payload.model_dump(exclude_unset=True))
    await session.commit()
    return envelope(request, HonorRead.model_validate(row))


@router.delete("/{profile_id}/honors/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_honor(
    profile_id: uuid.UUID,
    item_id: uuid.UUID,
    session: SessionDependency,
    user: CurrentUserDependency,
) -> None:
    await owned_profile(session, profile_id, user.id)
    await session.delete(await owned_child(session, Honor, item_id, profile_id))
    await session.commit()


@router.post("/{profile_id}/evaluate/honors")
async def evaluate_saved_honors(
    profile_id: uuid.UUID, request: Request, session: SessionDependency, user: CurrentUserDependency
) -> dict[str, object]:
    profile = await owned_profile(session, profile_id, user.id)
    rows = list(await session.scalars(select(Honor).where(Honor.profile_id == profile_id)))
    if not rows:
        raise NotFoundError("Add honors before evaluating")
    results = [evaluate_honor(honor_input_from_saved(row, profile.intended_major)) for row in rows]
    for row, result in zip(rows, results, strict=True):
        await persist_evaluation(
            session,
            user_id=user.id,
            profile_id=profile_id,
            evaluation_type="HONOR",
            input_data={"honor_id": str(row.id)},
            result=result,
            subject_entity_id=row.id,
        )
    await session.commit()
    return envelope(request, {"evaluations": results})


@router.get("/{profile_id}/essays")
async def list_essays(
    profile_id: uuid.UUID,
    request: Request,
    session: SessionDependency,
    user: CurrentUserDependency,
) -> dict[str, object]:
    await owned_profile(session, profile_id, user.id)
    rows = list(
        await session.scalars(
            select(Essay)
            .where(Essay.profile_id == profile_id, Essay.user_id == user.id)
            .order_by(Essay.created_at.desc())
        )
    )
    evaluations = (
        list(
            await session.scalars(
                select(Evaluation)
                .where(
                    Evaluation.user_id == user.id,
                    Evaluation.evaluation_type == "ESSAY",
                    Evaluation.subject_entity_id.in_([row.id for row in rows]),
                )
                .order_by(Evaluation.evaluated_at.desc())
            )
        )
        if rows
        else []
    )
    evaluation_by_essay: dict[uuid.UUID, Evaluation] = {}
    for evaluation in evaluations:
        if evaluation.subject_entity_id is not None:
            evaluation_by_essay.setdefault(evaluation.subject_entity_id, evaluation)
    return envelope(
        request,
        [
            SavedEssayHistoryItem(
                **SavedEssayRead.model_validate(row).model_dump(),
                evaluation_id=evaluation_by_essay[row.id].id
                if row.id in evaluation_by_essay
                else None,
                display_score=evaluation_by_essay[row.id].display_score
                if row.id in evaluation_by_essay
                else None,
                confidence=evaluation_by_essay[row.id].confidence
                if row.id in evaluation_by_essay
                else None,
            )
            for row in rows
        ],
    )


@router.post("/{profile_id}/essays", status_code=status.HTTP_201_CREATED)
async def create_essay(
    profile_id: uuid.UUID,
    payload: SavedEssayCreate,
    request: Request,
    session: SessionDependency,
    user: CurrentUserDependency,
) -> dict[str, object]:
    await owned_profile(session, profile_id, user.id)
    evaluation = evaluate_essay(
        EssayEvaluationRequest(
            essay_type=payload.essay_type,
            text=payload.text,
            min_words=payload.min_words,
            word_limit=payload.word_limit,
            prompt_text=payload.prompt_text,
        )
    )
    row = Essay(
        profile_id=profile_id,
        user_id=user.id,
        essay_type=payload.essay_type,
        title=payload.title,
        prompt_text=payload.prompt_text,
        word_limit=payload.word_limit,
        min_words=payload.min_words,
        raw_text=payload.text if payload.save_raw_text else None,
        save_raw_text=payload.save_raw_text,
        content_hash=hashlib.sha256(payload.text.encode()).hexdigest(),
    )
    session.add(row)
    await session.flush()
    await persist_evaluation(
        session,
        user_id=user.id,
        profile_id=profile_id,
        evaluation_type="ESSAY",
        input_data={"content_hash": row.content_hash, "essay_type": row.essay_type},
        result=evaluation,
        subject_entity_id=row.id,
    )
    await session.commit()
    await session.refresh(row)
    return envelope(
        request,
        {"essay": SavedEssayRead.model_validate(row), "evaluation": evaluation},
    )


@router.get("/{profile_id}/essays/{item_id}")
async def get_essay(
    profile_id: uuid.UUID,
    item_id: uuid.UUID,
    request: Request,
    session: SessionDependency,
    user: CurrentUserDependency,
) -> dict[str, object]:
    await owned_profile(session, profile_id, user.id)
    row = await owned_child(session, Essay, item_id, profile_id)
    if row.user_id != user.id:
        raise NotFoundError("Essay not found")
    evaluation = await session.scalar(
        select(Evaluation)
        .where(
            Evaluation.user_id == user.id,
            Evaluation.profile_id == profile_id,
            Evaluation.subject_entity_id == row.id,
            Evaluation.evaluation_type == "ESSAY",
        )
        .order_by(Evaluation.evaluated_at.desc())
        .limit(1)
    )
    evaluation_detail: dict[str, object] | None = None
    if evaluation is not None:
        components = list(
            await session.scalars(
                select(EvaluationComponent).where(
                    EvaluationComponent.evaluation_id == evaluation.id
                )
            )
        )
        rules = list(
            await session.scalars(
                select(TriggeredRule)
                .where(TriggeredRule.evaluation_id == evaluation.id)
                .order_by(TriggeredRule.rule_id)
            )
        )
        severity_rank = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
        rules.sort(key=lambda item: (severity_rank.get(item.severity, 5), item.rule_id))
        metrics = await session.scalar(
            select(EssayMetric)
            .where(EssayMetric.essay_id == row.id)
            .order_by(EssayMetric.created_at.desc())
            .limit(1)
        )
        evaluation_detail = {
            "id": evaluation.id,
            "engine_version": evaluation.engine_version,
            "rubric_version": evaluation.rubric_version,
            "overall_score": evaluation.overall_score,
            "display_score": evaluation.display_score,
            "confidence": evaluation.confidence,
            "components": {
                item.component_name: item.score for item in components
            },
            "issues": [
                {
                    "rule_id": item.rule_id,
                    "severity": item.severity,
                    "message": item.message,
                    "evidence": item.evidence,
                }
                for item in rules
            ],
            "metrics": (
                {
                    "word_count": metrics.word_count,
                    "character_count": metrics.character_count,
                    "sentence_count": metrics.sentence_count,
                    "paragraph_count": metrics.paragraph_count,
                    "average_sentence_length": metrics.avg_sentence_length,
                    "flesch_reading_ease": metrics.flesch_reading_ease,
                    "lexical_diversity": metrics.lexical_diversity,
                    "reflection_density": metrics.reflection_density,
                    "specificity_density": metrics.specificity_density,
                }
                if metrics is not None
                else None
            ),
        }
    return envelope(
        request,
        {"essay": SavedEssayRead.model_validate(row), "evaluation": evaluation_detail},
    )


@router.delete("/{profile_id}/essays/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_essay(
    profile_id: uuid.UUID,
    item_id: uuid.UUID,
    session: SessionDependency,
    user: CurrentUserDependency,
) -> None:
    await owned_profile(session, profile_id, user.id)
    row = await owned_child(session, Essay, item_id, profile_id)
    if row.user_id != user.id:
        raise NotFoundError("Essay not found")
    await session.execute(
        delete(Evaluation).where(
            Evaluation.user_id == user.id,
            Evaluation.evaluation_type == "ESSAY",
            Evaluation.subject_entity_id == row.id,
        )
    )
    await session.delete(row)
    await session.commit()


@router.get("/{profile_id}/recommendations")
async def list_recommendations(
    profile_id: uuid.UUID, request: Request, session: SessionDependency, user: CurrentUserDependency
) -> dict[str, object]:
    await owned_profile(session, profile_id, user.id)
    rows = list(
        await session.scalars(
            select(Recommendation).where(
                Recommendation.profile_id == profile_id, Recommendation.user_id == user.id
            )
        )
    )
    return envelope(request, [SavedRecommendationRead.model_validate(row) for row in rows])


@router.post("/{profile_id}/recommendations", status_code=status.HTTP_201_CREATED)
async def create_recommendation(
    profile_id: uuid.UUID,
    payload: SavedRecommendationCreate,
    request: Request,
    session: SessionDependency,
    user: CurrentUserDependency,
) -> dict[str, object]:
    await owned_profile(session, profile_id, user.id)
    evaluation = evaluate_lor(
        LorEvaluationRequest(
            text=payload.text,
            recommender_role=payload.recommender_role,
            relationship_duration_months=payload.relationship_duration_months,
            instructional_context=payload.instructional_context,
        )
    )
    content_hash = hashlib.sha256(payload.text.encode()).hexdigest()
    row = Recommendation(
        profile_id=profile_id,
        user_id=user.id,
        recommender_role=payload.recommender_role,
        relationship_duration_months=payload.relationship_duration_months,
        raw_text=payload.text if payload.save_raw_text else None,
        save_raw_text=payload.save_raw_text,
        content_hash=content_hash,
    )
    session.add(row)
    await session.flush()
    await persist_evaluation(
        session,
        user_id=user.id,
        profile_id=profile_id,
        evaluation_type="LOR",
        input_data={"content_hash": content_hash},
        result=evaluation,
        subject_entity_id=row.id,
    )
    await session.commit()
    await session.refresh(row)
    return envelope(
        request,
        {"recommendation": SavedRecommendationRead.model_validate(row), "evaluation": evaluation},
    )


@router.delete("/{profile_id}/recommendations/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recommendation(
    profile_id: uuid.UUID,
    item_id: uuid.UUID,
    session: SessionDependency,
    user: CurrentUserDependency,
) -> None:
    await owned_profile(session, profile_id, user.id)
    row = await owned_child(session, Recommendation, item_id, profile_id)
    if row.user_id != user.id:
        raise NotFoundError("Recommendation not found")
    await session.execute(
        delete(Evaluation).where(
            Evaluation.user_id == user.id,
            Evaluation.evaluation_type == "LOR",
            Evaluation.subject_entity_id == row.id,
        )
    )
    await session.delete(row)
    await session.commit()


@router.get("/{profile_id}/targets")
async def list_targets(
    profile_id: uuid.UUID, request: Request, session: SessionDependency, user: CurrentUserDependency
) -> dict[str, object]:
    await owned_profile(session, profile_id, user.id)
    rows = (
        await session.execute(
            select(TargetCollege, College)
            .join(College, College.id == TargetCollege.college_id)
            .where(TargetCollege.profile_id == profile_id)
            .order_by(TargetCollege.priority, TargetCollege.id)
        )
    ).all()
    return envelope(
        request,
        [
            TargetWithCollege(
                **TargetRead.model_validate(target).model_dump(),
                college_name=college.name,
                college_slug=college.slug,
            )
            for target, college in rows
        ],
    )


@router.post("/{profile_id}/targets", status_code=status.HTTP_201_CREATED)
async def create_target(
    profile_id: uuid.UUID,
    payload: TargetWrite,
    request: Request,
    session: SessionDependency,
    user: CurrentUserDependency,
) -> dict[str, object]:
    await owned_profile(session, profile_id, user.id)
    if await session.get(College, payload.college_id) is None:
        raise NotFoundError("College not found")
    existing = await session.scalar(
        select(TargetCollege).where(
            TargetCollege.profile_id == profile_id, TargetCollege.college_id == payload.college_id
        )
    )
    if existing is not None:
        raise DomainError("College is already a target", code="DUPLICATE_TARGET")
    row = TargetCollege(profile_id=profile_id, **payload.model_dump())
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return envelope(request, TargetRead.model_validate(row))


@router.patch("/{profile_id}/targets/{item_id}")
async def update_target(
    profile_id: uuid.UUID,
    item_id: uuid.UUID,
    payload: TargetPatch,
    request: Request,
    session: SessionDependency,
    user: CurrentUserDependency,
) -> dict[str, object]:
    await owned_profile(session, profile_id, user.id)
    row = await owned_child(session, TargetCollege, item_id, profile_id)
    apply_patch(row, payload.model_dump(exclude_unset=True))
    await session.commit()
    await session.refresh(row)
    return envelope(request, TargetRead.model_validate(row))


@router.delete("/{profile_id}/targets/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_target(
    profile_id: uuid.UUID,
    item_id: uuid.UUID,
    session: SessionDependency,
    user: CurrentUserDependency,
) -> None:
    await owned_profile(session, profile_id, user.id)
    await session.delete(await owned_child(session, TargetCollege, item_id, profile_id))
    await session.commit()


async def _academic_evaluation(
    session: AsyncSession, profile: ApplicantProfile
) -> AcademicEvaluationResponse | None:
    terms = list(
        await session.scalars(
            select(AcademicTerm)
            .where(AcademicTerm.profile_id == profile.id)
            .order_by(AcademicTerm.term_order)
        )
    )
    if not terms:
        return None
    courses = list(await session.scalars(select(Course).where(Course.profile_id == profile.id)))
    school_context = await session.scalar(
        select(SchoolContext).where(SchoolContext.profile_id == profile.id)
    )
    result = evaluate_academic(
        AcademicEvaluationRequest(
            terms=[
                AcademicTermInput(term_order=row.term_order, average_grade=row.average_grade)
                for row in terms
            ],
            courses=[
                CourseInput(
                    grade_value=row.grade_value, is_major_related=bool(row.is_major_related)
                )
                for row in courses
            ],
            scale_min=float(profile.grading_scale_min)
            if profile.grading_scale_min is not None
            else None,
            scale_max=float(profile.grading_scale_max)
            if profile.grading_scale_max is not None
            else None,
            class_rank=profile.class_rank,
            class_size=profile.class_size,
            rigor_evidence=rigor_from_saved_courses(courses, school_context),
        )
    )
    return result


def cds_application_component(factor_name: str) -> str | None:
    """Map Common Data Set factor labels to Evalio's measurable components."""
    name = " ".join(factor_name.casefold().replace("/", " ").replace("_", " ").split())
    if any(token in name for token in ("rigor", "academic gpa", "class rank", "academic record")):
        return "academics"
    if "standardized test" in name or "test score" in name:
        return "testing"
    if "essay" in name:
        return "essay"
    if "recommend" in name:
        return "recommendations"
    if any(token in name for token in ("extracurricular", "volunteer", "work experience")):
        return "activities"
    if any(token in name for token in ("talent", "honor", "award")):
        return "honors"
    return None


def select_college_test(tests: list[TestScore]) -> TestScore | None:
    return next(
        (
            item
            for item in tests
            if item.composite_score is not None
            and item.test_type.upper() in {"SAT", "ACT"}
        ),
        None,
    )


async def _application_component_scores(
    session: AsyncSession,
    profile: ApplicantProfile,
    academic_strength: float | None,
) -> dict[str, float]:
    profile_id = profile.id
    scores: dict[str, float] = {}
    if academic_strength is not None:
        scores["academics"] = academic_strength

    activities = list(
        await session.scalars(
            select(Activity)
            .where(Activity.profile_id == profile_id)
            .order_by(Activity.activity_order, Activity.id)
        )
    )
    if activities:
        activity_result = evaluate_activities(
            ActivityEvaluationRequest(
                activities=[activity_input_from_saved(row) for row in activities]
            )
        )
        scores["activities"] = activity_result.portfolio_score

    honors = list(await session.scalars(select(Honor).where(Honor.profile_id == profile_id)))
    honor_scores = [
        evaluate_honor(honor_input_from_saved(row, profile.intended_major)).overall_score
        for row in honors
    ]
    if honor_scores:
        scores["honors"] = max(honor_scores)

    evaluations = list(
        await session.scalars(
            select(Evaluation)
            .where(
                Evaluation.profile_id == profile_id,
                Evaluation.evaluation_type.in_(["ESSAY", "LOR"]),
                Evaluation.overall_score.is_not(None),
            )
            .order_by(Evaluation.evaluated_at.desc())
        )
    )
    for evaluation in evaluations:
        key = "essay" if evaluation.evaluation_type == "ESSAY" else "recommendations"
        if key not in scores and evaluation.overall_score is not None:
            scores[key] = float(evaluation.overall_score)
    return scores


@router.post("/{profile_id}/colleges/{college_id}/evaluate")
async def evaluate_saved_college(
    profile_id: uuid.UUID,
    college_id: uuid.UUID,
    payload: EvaluationDate,
    request: Request,
    session: SessionDependency,
    user: CurrentUserDependency,
) -> dict[str, object]:
    profile = await owned_profile(session, profile_id, user.id)
    college = await session.get(College, college_id)
    if college is None or not college.active:
        raise NotFoundError("College not found")
    admission = await session.scalar(
        select(CollegeAdmissions)
        .where(CollegeAdmissions.college_id == college_id)
        .order_by(CollegeAdmissions.academic_cycle.desc())
        .limit(1)
    )
    financial = await session.scalar(
        select(CollegeFinancialAid)
        .where(CollegeFinancialAid.college_id == college_id)
        .order_by(CollegeFinancialAid.academic_cycle.desc())
        .limit(1)
    )
    cds_cycle = await session.scalar(
        select(func.max(CollegeCdsFactor.academic_cycle)).where(
            CollegeCdsFactor.college_id == college_id
        )
    )
    cds_factors = (
        list(
            await session.scalars(
                select(CollegeCdsFactor).where(
                    CollegeCdsFactor.college_id == college_id,
                    CollegeCdsFactor.academic_cycle == cds_cycle,
                )
            )
        )
        if cds_cycle is not None
        else []
    )
    sources = list(
        await session.scalars(select(CollegeSource).where(CollegeSource.college_id == college_id))
    )
    latest_requirement_cycle = await session.scalar(
        select(func.max(CollegeRequirement.academic_cycle)).where(
            CollegeRequirement.college_id == college_id
        )
    )
    requirements = list(
        await session.scalars(
            select(CollegeRequirement).where(
                CollegeRequirement.college_id == college_id,
                CollegeRequirement.academic_cycle == latest_requirement_cycle,
            )
        )
    )
    material_statuses = list(
        await session.scalars(
            select(ApplicationMaterialStatus).where(
                ApplicationMaterialStatus.profile_id == profile_id,
                ApplicationMaterialStatus.college_id == college_id,
            )
        )
    )
    completion_by_type = {
        item.requirement_type: item.completion_status for item in material_statuses
    }
    required_materials = [item for item in requirements if item.status == "REQUIRED"]
    required_materials_complete = all(
        completion_by_type.get(item.requirement_type) in {"PRESENT", "SUBMITTED", "NOT_APPLICABLE"}
        for item in required_materials
    )
    tests = list(
        await session.scalars(
            select(TestScore)
            .where(TestScore.profile_id == profile_id)
            .order_by(TestScore.test_date.desc().nullslast())
        )
    )
    test = select_college_test(tests)
    test_range = None
    if admission and test:
        values = (
            (admission.sat_25, admission.sat_50, admission.sat_75)
            if test.test_type.upper().startswith("SAT")
            else (admission.act_25, admission.act_50, admission.act_75)
        )
        if all(value is not None for value in values):
            test_range = PublishedRange(
                lower=float(cast(Decimal, values[0])),
                median=float(cast(Decimal, values[1])),
                upper=float(cast(Decimal, values[2])),
            )
    profile_fields = [
        profile.country_code,
        profile.graduation_year,
        profile.curriculum_type,
        profile.intended_major,
        profile.school_name,
        profile.grading_scale_min,
        profile.grading_scale_max,
    ]
    profile_completeness = sum(value is not None for value in profile_fields) * 5
    critical_markers = (
        "deadline",
        "test",
        "essay",
        "recommend",
        "aid",
        "tuition",
        "cost",
    )
    critical_sources = [
        source
        for source in sources
        if any(
            marker in f"{source.field_group} {source.field_name}".casefold()
            for marker in critical_markers
        )
    ]
    critical_dates = [source.verified_at or source.retrieved_at for source in critical_sources]
    oldest_critical = min(critical_dates, default=None)
    evaluation_moment = datetime.combine(payload.evaluation_date, time.min, tzinfo=UTC)
    age = (evaluation_moment - oldest_critical).days if oldest_critical else None
    financial_dates = [
        source.verified_at or source.retrieved_at
        for source in sources
        if any(
            marker in f"{source.field_group} {source.field_name}".casefold()
            for marker in ("financial", "aid", "tuition", "cost")
        )
    ]
    oldest_financial = min(financial_dates, default=None)
    financial_age = (
        (evaluation_moment - oldest_financial).days if oldest_financial else None
    )
    freshness_points = (
        25 if age is not None and age <= 365 else 15 if age is not None and age <= 730 else 0
    )
    data_completeness = min(
        20, (8 if admission else 0) + (6 if requirements else 0) + (6 if financial else 0)
    )
    reliability = min(20, sum(5 if source.confidence == "HIGH" else 3 for source in sources))
    academic_result = await _academic_evaluation(session, profile)
    academic_strength = academic_result.overall_score if academic_result else None
    application_components = await _application_component_scores(
        session, profile, academic_strength
    )
    importance_rank = {
        "UNKNOWN": -1,
        "NOT_CONSIDERED": 0,
        "CONSIDERED": 1,
        "IMPORTANT": 2,
        "VERY_IMPORTANT": 3,
    }
    cds_importance: dict[str, str] = {}
    unmapped_cds_factors = 0
    for factor in cds_factors:
        component = cds_application_component(factor.factor_name)
        importance = factor.importance.upper()
        if importance not in importance_rank:
            unmapped_cds_factors += 1
            continue
        if component is None:
            if importance != "NOT_CONSIDERED":
                unmapped_cds_factors += 1
            continue
        current = cds_importance.get(component)
        if current is None or importance_rank[importance] > importance_rank[current]:
            cds_importance[component] = importance
    college_result = evaluate_college(
        CollegeEvaluationRequest(
            academic_strength=academic_strength,
            applicant_test_score=float(test.composite_score)
            if test and test.composite_score is not None
            else None,
            published_test_range=test_range,
            test_policy=cast(Any, admission.test_policy if admission else "UNKNOWN"),
            acceptance_rate=float(admission.acceptance_rate)
            if admission and admission.acceptance_rate is not None
            else None,
            requirements_known=bool(requirements),
            required_materials_complete=required_materials_complete,
            profile_completeness=profile_completeness,
            source_freshness_points=freshness_points,
            college_data_completeness=data_completeness,
            metric_reliability=reliability,
            critical_source_stale=age is None
            or age > 730
            or any(source.freshness in {"STALE", "UNKNOWN"} for source in critical_sources),
            multiple_critical_unknown=admission is None and financial is None,
            application_components=cast(Any, application_components),
            cds_importance=cast(Any, cds_importance),
            unmapped_cds_factors=unmapped_cds_factors,
        )
    )
    financial_result = evaluate_financial(
        FinancialEvaluationRequest(
            applicant_type=cast(Any, str(profile.applicant_type)),
            requires_substantial_aid=bool(profile.requires_need_based_aid),
            max_family_contribution=float(profile.max_family_contribution)
            if profile.max_family_contribution is not None
            else None,
            need_policy=cast(Any, financial.need_policy if financial else "UNKNOWN"),
            international_need_based_aid=financial.international_need_based_aid
            if financial
            else None,
            cost_freshness=cast(
                Any,
                "CURRENT"
                if financial_age is not None and financial_age <= 365
                else "STALE"
                if financial_age is not None
                else "UNKNOWN",
            ),
        )
    )
    data = college_result.model_dump(mode="json")
    data.update(
        college={"id": str(college.id), "slug": college.slug, "name": college.name},
        course_rigor=academic_result.components.rigor if academic_result else None,
        financial_fit=financial_result.fit,
        financial_risk=financial_result.risk,
        financial_confidence=financial_result.confidence,
        financial_reasons=financial_result.reasons,
        college_data_cycles={
            "admissions": admission.academic_cycle if admission else None,
            "requirements": latest_requirement_cycle,
            "financial_aid": financial.academic_cycle if financial else None,
            "cds": cds_cycle,
        },
        source_freshness=(
            "UNKNOWN"
            if not critical_sources
            else "STALE"
            if age is None
            or age > 730
            or any(source.freshness == "STALE" for source in critical_sources)
            else "REVIEW_SOON"
            if age > 365 or any(source.freshness == "UNKNOWN" for source in critical_sources)
            else "CURRENT"
        ),
        oldest_critical_source_at=oldest_critical.isoformat() if oldest_critical else None,
        evaluation_date=payload.evaluation_date.isoformat(),
    )
    await persist_evaluation(
        session,
        user_id=user.id,
        profile_id=profile_id,
        evaluation_type="COLLEGE",
        input_data={
            "college_id": str(college_id),
            "evaluation_date": payload.evaluation_date.isoformat(),
        },
        result=college_result,
        college_id=college_id,
        evaluation_date=payload.evaluation_date,
    )
    await session.commit()
    return envelope(request, data)


@router.get("/{profile_id}/colleges/{college_id}/materials")
async def list_material_statuses(
    profile_id: uuid.UUID,
    college_id: uuid.UUID,
    request: Request,
    session: SessionDependency,
    user: CurrentUserDependency,
) -> dict[str, object]:
    await owned_profile(session, profile_id, user.id)
    if await session.get(College, college_id) is None:
        raise NotFoundError("College not found")
    rows = list(
        await session.scalars(
            select(ApplicationMaterialStatus)
            .where(
                ApplicationMaterialStatus.profile_id == profile_id,
                ApplicationMaterialStatus.college_id == college_id,
            )
            .order_by(ApplicationMaterialStatus.requirement_type)
        )
    )
    return envelope(request, [MaterialStatusRead.model_validate(row) for row in rows])


@router.put("/{profile_id}/colleges/{college_id}/materials")
async def replace_material_statuses(
    profile_id: uuid.UUID,
    college_id: uuid.UUID,
    payload: list[MaterialStatusWrite],
    request: Request,
    session: SessionDependency,
    user: CurrentUserDependency,
) -> dict[str, object]:
    await owned_profile(session, profile_id, user.id)
    if len(payload) > 100:
        raise DomainError("An audit may contain at most 100 materials", code="LIMIT_EXCEEDED")
    if await session.get(College, college_id) is None:
        raise NotFoundError("College not found")
    types = [item.requirement_type for item in payload]
    if len(types) != len(set(types)):
        raise DomainError("Duplicate requirement type", code="DUPLICATE_ITEM")
    await session.execute(
        delete(ApplicationMaterialStatus).where(
            ApplicationMaterialStatus.profile_id == profile_id,
            ApplicationMaterialStatus.college_id == college_id,
        )
    )
    rows = [
        ApplicationMaterialStatus(
            profile_id=profile_id,
            college_id=college_id,
            **item.model_dump(mode="json"),
        )
        for item in payload
    ]
    session.add_all(rows)
    await session.commit()
    for row in rows:
        await session.refresh(row)
    return envelope(request, [MaterialStatusRead.model_validate(row) for row in rows])


@router.post("/{profile_id}/colleges/{college_id}/audit")
async def audit_saved_application(
    profile_id: uuid.UUID,
    college_id: uuid.UUID,
    payload: EvaluationDate,
    request: Request,
    session: SessionDependency,
    user: CurrentUserDependency,
) -> dict[str, object]:
    await owned_profile(session, profile_id, user.id)
    if await session.get(College, college_id) is None:
        raise NotFoundError("College not found")
    latest_cycle = await session.scalar(
        select(func.max(CollegeRequirement.academic_cycle)).where(
            CollegeRequirement.college_id == college_id
        )
    )
    requirements = list(
        await session.scalars(
            select(CollegeRequirement).where(
                CollegeRequirement.college_id == college_id,
                CollegeRequirement.academic_cycle == latest_cycle,
            )
        )
    )
    statuses = list(
        await session.scalars(
            select(ApplicationMaterialStatus).where(
                ApplicationMaterialStatus.profile_id == profile_id,
                ApplicationMaterialStatus.college_id == college_id,
            )
        )
    )
    by_type = {item.requirement_type: item for item in statuses}
    materials = [
        MaterialStatus(
            requirement_type=item.requirement_type,
            requirement_status=cast(
                Any,
                item.status
                if item.status in {"REQUIRED", "OPTIONAL", "RECOMMENDED", "NOT_REQUIRED", "UNKNOWN"}
                else "UNKNOWN",
            ),
            completion_status=cast(
                Any,
                by_type[item.requirement_type].completion_status
                if item.requirement_type in by_type
                else "MISSING",
            ),
            deadline=item.deadline,
            quality_evaluated=(
                by_type[item.requirement_type].linked_entity_id is not None
                if item.requirement_type in by_type
                else False
            ),
        )
        for item in requirements
    ]
    result = audit_application(
        ApplicationAuditRequest(evaluation_date=payload.evaluation_date, materials=materials)
    )
    await persist_evaluation(
        session,
        user_id=user.id,
        profile_id=profile_id,
        evaluation_type="APPLICATION",
        input_data={
            "college_id": str(college_id),
            "evaluation_date": payload.evaluation_date.isoformat(),
        },
        result=result,
        college_id=college_id,
        evaluation_date=payload.evaluation_date,
    )
    await session.commit()
    return envelope(request, {"audit": result})


@router.get("/{profile_id}/evaluations")
async def list_evaluations(
    profile_id: uuid.UUID, request: Request, session: SessionDependency, user: CurrentUserDependency
) -> dict[str, object]:
    await owned_profile(session, profile_id, user.id)
    rows = list(
        await session.scalars(
            select(Evaluation)
            .where(Evaluation.profile_id == profile_id, Evaluation.user_id == user.id)
            .order_by(Evaluation.evaluated_at.desc())
            .limit(100)
        )
    )
    return envelope(request, [EvaluationRead.model_validate(row) for row in rows])
