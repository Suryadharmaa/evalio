ENGINE_VERSION = "2.0.0"
RULEBOOK_VERSION = "2.0.0"
SCHEMA_REVISION = "20260923_0011"

# Existing persisted evaluations use these rubric versions. Keep this mapping
# unchanged until the V2 rollout switch is explicitly enabled.
V1_RUBRIC_VERSIONS = {
    "application": "application-1.1.0",
    "academic": "academic-1.1.0",
    "activity": "activity-1.1.0",
    "activity_description": "activity-description-1.0.0",
    "college": "college-1.1.0",
    "essay": "essay-1.0.0",
    "honor": "honor-1.1.0",
    "lor": "lor-1.0.0",
}

V2_RUBRIC_VERSIONS = {
    "academic": "academic-2.0.0",
    "coursework": "coursework-2.0.0",
    "testing": "testing-2.0.0",
    "activity": "activity-2.0.0",
    "activity_description": "activity-description-2.0.0",
    "honor": "honor-2.0.0",
    "essay": "essay-craft-2.0.0",
    "writing_patterns": "writing-patterns-2.0.0",
    "lor": "lor-2.0.0",
    "college": "college-alignment-2.0.0",
    "financial": "financial-fit-2.0.0",
    "scholarship": "scholarship-eligibility-2.0.0",
    "application": "application-audit-2.0.0",
    "confidence": "confidence-2.0.0",
    "profile": "profile-evidence-2.0.0",
}

# Backward-compatible export used by every current V1 route.
RUBRIC_VERSIONS = V1_RUBRIC_VERSIONS


def rubric_versions_for(track: str) -> dict[str, str]:
    if track == "v1":
        return dict(V1_RUBRIC_VERSIONS)
    if track == "v2":
        return dict(V2_RUBRIC_VERSIONS)
    raise ValueError(f"Unsupported scoring engine track: {track}")
