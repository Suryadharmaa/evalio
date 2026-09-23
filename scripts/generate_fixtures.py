"""Generate deterministic, synthetic-only calibration fixtures."""

import json
from pathlib import Path

ROOT = Path("tests/fixtures")


def write(name: str, rows: list[dict[str, object]]) -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    (ROOT / name).write_text(json.dumps(rows, indent=2, sort_keys=True), encoding="utf-8")


def main() -> None:
    essays = [
        {
            "id": f"essay-{index:02d}",
            "essay_type": "COMMON_APP",
            "min_words": 0,
            "word_limit": 650,
            "text": f"In September 202{index % 6}, I built project Atlas {index}. I learned that careful measurement changes how I solve problems.\n\nAfter testing it with {10 + index} students, I revised the process and documented the result.",
        }
        for index in range(1, 31)
    ]
    academics = [
        {
            "id": f"academic-{index:02d}",
            "scale_min": 0,
            "scale_max": 100,
            "terms": [
                {"term_order": term, "average_grade": 70 + index % 20 + term}
                for term in range(1, 5)
            ],
        }
        for index in range(1, 21)
    ]
    activities = [
        {
            "id": f"activities-{index:02d}",
            "activities": [
                {
                    "activity_name": f"Project {index}",
                    "people_impacted": index * 10,
                    "duration_months": 6 + index,
                    "hours_per_week": 3,
                    "leadership_level": "LEAD",
                    "initiative_level": "STARTED_PROJECT",
                    "recognition_scope": "SCHOOL_LOCAL",
                    "progression_level": "CLEAR",
                }
            ],
        }
        for index in range(1, 21)
    ]
    lors = [
        {
            "id": f"lor-{index:02d}",
            "recommender_role": "Teacher",
            "relationship_duration_months": 12 + index,
            "text": f"I taught this student for two semesters. During project {index}, the student researched evidence and supported the team. Among the strongest students in my {5 + index} years.",
        }
        for index in range(1, 11)
    ]
    colleges = [
        {
            "id": f"college-{index:02d}",
            "academic_strength": 60 + index,
            "application_components": {
                "activities": 55 + index,
                "essay": 60 + index,
            },
            "cds_importance": {
                "academics": "VERY_IMPORTANT",
                "activities": "IMPORTANT",
                "essay": "CONSIDERED",
                "recommendations": "UNKNOWN" if index % 5 == 0 else "NOT_CONSIDERED",
            },
            "acceptance_rate": index / 100,
            "required_materials_complete": index % 4 != 0,
            "profile_completeness": 30,
            "source_freshness_points": 22,
            "college_data_completeness": 18,
            "metric_reliability": 18,
        }
        for index in range(1, 21)
    ]
    honors = [
        {
            "id": f"honor-{index:02d}",
            "honor_name": f"Synthetic Award {index}",
            "scope": "SCHOOL",
            "placement": "TOP_10",
            "academic_relevance": 10,
            "repeat_count": 1,
        }
        for index in range(1, 21)
    ]
    write("essays.json", essays)
    write("academics.json", academics)
    write("activities.json", activities)
    write("lors.json", lors)
    write("colleges.json", colleges)
    write("honors.json", honors)


if __name__ == "__main__":
    main()
