from api.admission_engine.schemas.lor_builder import (
    LorBuildRequest,
    LorBuildResponse,
    LorFrameworkItem,
    LorFrameworkSection,
)

ENDORSEMENT_SHELLS = {
    "MEASURED": "Based on the evidence above, I recommend [student_name] for consideration.",
    "CLEAR": "Based on the evidence above, I am pleased to recommend [student_name].",
    "STRONG": "Based on the evidence above, I strongly recommend [student_name].",
    "WITHOUT_RESERVATION": "Based on the evidence above, I recommend [student_name] without reservation.",
}


def evidence(text: str, *source_fields: str) -> LorFrameworkItem:
    return LorFrameworkItem(
        item_type="USER_EVIDENCE", text=text, source_fields=list(source_fields)
    )


def shell(text: str, *source_fields: str) -> LorFrameworkItem:
    return LorFrameworkItem(
        item_type="SENTENCE_SHELL", text=text, source_fields=list(source_fields)
    )


def prompt(text: str) -> LorFrameworkItem:
    return LorFrameworkItem(item_type="WRITING_PROMPT", text=text, source_fields=[])


def build_lor_framework(request: LorBuildRequest) -> LorBuildResponse:
    opening = [
        evidence(f"Recommender role: {request.recommender_role}", "recommender_role"),
        evidence(f"Student: {request.student_name}", "student_name"),
        evidence(f"Relationship: {request.relationship_context}", "relationship_context"),
        evidence(f"Duration: {request.relationship_duration}", "relationship_duration"),
        shell(
            "In my role as [recommender_role], I have known [student_name] for "
            "[relationship_duration] through [relationship_context].",
            "recommender_role",
            "student_name",
            "relationship_duration",
            "relationship_context",
        ),
    ]
    if request.subject_or_context:
        opening.insert(4, evidence(request.subject_or_context, "subject_or_context"))

    body_1 = [
        evidence(f"Quality to demonstrate: {request.qualities[0]}", "qualities[0]"),
        evidence(request.specific_examples[0], "specific_examples[0]"),
    ]
    if request.academic_evidence:
        body_1.append(evidence(request.academic_evidence, "academic_evidence"))
    else:
        body_1.append(prompt("[Add academic or professional evidence only if directly observed.]"))
    body_1.append(
        shell(
            "During [relationship_context], I observed [student_name] demonstrate "
            "[quality] when [specific_example].",
            "relationship_context",
            "student_name",
            "qualities[0]",
            "specific_examples[0]",
        )
    )

    second_quality = request.qualities[1] if len(request.qualities) > 1 else request.qualities[0]
    body_2 = [evidence(f"Quality to demonstrate: {second_quality}", "qualities")]
    if len(request.specific_examples) > 1:
        body_2.append(evidence(request.specific_examples[1], "specific_examples[1]"))
    else:
        body_2.append(prompt("[Add a distinct, directly observed character or community anecdote.]"))
    if request.community_evidence:
        body_2.append(evidence(request.community_evidence, "community_evidence"))
    else:
        body_2.append(prompt("[Add community evidence only if directly observed.]"))
    body_2.append(
        shell(
            "A separate example of [quality] occurred when [specific community anecdote].",
            "qualities",
            "specific_examples",
            "community_evidence",
        )
    )

    body_3 = [
        evidence(item, f"specific_examples[{index}]")
        for index, item in enumerate(request.specific_examples[2:], 2)
    ]
    if request.comparative_evidence:
        body_3.insert(0, evidence(request.comparative_evidence, "comparative_evidence"))
    else:
        body_3.insert(0, prompt("[Add a comparative claim only if the recommender can substantiate it.]"))
    body_3.append(prompt("[Explain growth or progression using only the supplied examples.]"))

    closing = [
        evidence(
            f"Selected endorsement strength: {request.endorsement_strength}",
            "endorsement_strength",
        ),
        shell(
            ENDORSEMENT_SHELLS[request.endorsement_strength],
            "endorsement_strength",
            "student_name",
        ),
        prompt("[Close with an invitation for follow-up in the recommender's own voice.]"),
    ]

    missing = [
        field
        for field, value in (
            ("subject_or_context", request.subject_or_context),
            ("academic_evidence", request.academic_evidence),
            ("community_evidence", request.community_evidence),
            ("comparative_evidence", request.comparative_evidence),
            ("second_specific_example", request.specific_examples[1:]),
        )
        if not value
    ]
    return LorBuildResponse(
        sections=[
            LorFrameworkSection(key="opening", title="Opening", purpose="Establish relationship, duration, and capacity.", items=opening),
            LorFrameworkSection(key="body_1", title="Body 1", purpose="Connect an academic or professional quality to evidence.", items=body_1),
            LorFrameworkSection(key="body_2", title="Body 2", purpose="Connect character or community contribution to a distinct anecdote.", items=body_2),
            LorFrameworkSection(key="body_3", title="Body 3", purpose="Add substantiated comparison and growth evidence.", items=body_3),
            LorFrameworkSection(key="closing", title="Closing", purpose="State the recommender-selected endorsement strength.", items=closing),
        ],
        missing_evidence=missing,
    )
