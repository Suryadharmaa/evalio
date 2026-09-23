"""Enrich Evalio's curated 200 colleges with latest federal College Scorecard data."""

from __future__ import annotations

import argparse
import csv
import io
import zipfile
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

SOURCE = Path("docs/evalio_top200_us_colleges.csv")
OUTPUT = Path("docs/evalio_top200_us_colleges_enriched.csv")
REPORT = Path("docs/evalio_top200_us_colleges_enriched_validation.md")
DEFAULT_SCORECARD_ZIP = Path(".evalio-staging/scorecard-2025.zip")
DEFAULT_FAIRTEST_CSV = Path(".evalio-staging/fairtest-2026-27.csv")
FAIRTEST_URL = "https://fairtest.org/test-optional-list/"
DATA_AS_OF = "2026-09-13"
OWNERSHIP = {1: "PUBLIC", 2: "PRIVATE_NONPROFIT", 3: "PRIVATE_FOR_PROFIT"}
NUMERIC_FIELDS = (
    "acceptance_rate", "sat_25", "sat_50", "sat_75", "act_25", "act_50", "act_75",
    "app_fee_usd", "tuition_usd", "estimated_cost_of_attendance_usd",
)
TEST_POLICIES = {"REQUIRED", "OPTIONAL", "FLEXIBLE", "BLIND", "UNKNOWN"}
AID_POLICIES = {"NEED_BLIND", "NEED_AWARE", "NO_NEED_BASED_AID", "UNKNOWN"}
MANUAL_UNIT_IDS = {
    "columbia-university": "190150",
    "university-of-pittsburgh": "215293",
    "virginia-tech": "233921",
    "the-cooper-union": "190372",
}
FAIRTEST_POLICY_MAP = {"Required": "REQUIRED", "Test Optional": "OPTIONAL", "Test Free": "BLIND"}
FAIRTEST_NAMES = {
    "arizona-state-university": "Arizona State University Campus Immersion",
    "columbia-university": "Columbia University in the City of New York",
    "university-of-washington": "University of Washington-Seattle Campus",
    "the-ohio-state-university": "Ohio State University-Main Campus",
    "virginia-tech": "Virginia Polytechnic Institute and State University",
    "tulane-university": "Tulane University of Louisiana",
    "university-of-cincinnati": "University of Cincinnati-Main Campus",
    "the-cooper-union": "The Cooper Union for the Advancement of Science and Art",
}


def normalized(value: str) -> str:
    return "".join(character.casefold() for character in value if character.isalnum())


def load_scorecard(path: Path) -> list[dict[str, Any]]:
    with zipfile.ZipFile(path) as archive:
        csv_name = next(name for name in archive.namelist() if name.lower().endswith(".csv"))
        with archive.open(csv_name) as raw:
            reader = csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8-sig", newline=""))
            return [
                {
                    "id": row["UNITID"], "school.name": row["INSTNM"],
                    "school.city": row["CITY"], "school.state": row["STABBR"],
                    "school.ownership": int(row["CONTROL"]) if row["CONTROL"].isdigit() else None,
                    "latest.admissions.admission_rate.overall": row["ADM_RATE"] or None,
                    "latest.admissions.sat_scores.25th_percentile.critical_reading": row["SATVR25"] or None,
                    "latest.admissions.sat_scores.25th_percentile.math": row["SATMT25"] or None,
                    "latest.admissions.sat_scores.75th_percentile.critical_reading": row["SATVR75"] or None,
                    "latest.admissions.sat_scores.75th_percentile.math": row["SATMT75"] or None,
                    "latest.admissions.act_scores.25th_percentile.cumulative": row["ACTCM25"] or None,
                    "latest.admissions.act_scores.75th_percentile.cumulative": row["ACTCM75"] or None,
                    "latest.cost.tuition.out_of_state": row["TUITIONFEE_OUT"] or None,
                    "latest.cost.attendance.academic_year": row["COSTT4_A"] or None,
                }
                for row in reader
                if row["CURROPER"] == "1"
            ]


def clean_source_url(value: str) -> str:
    parts = urlsplit(value)
    query = urlencode([(key, item) for key, item in parse_qsl(parts.query) if not key.startswith("utm_")])
    return urlunsplit((parts.scheme, parts.netloc, parts.path, query, parts.fragment))


def apply_fairtest(rows: list[dict[str, str]], path: Path) -> list[str]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        policies = list(csv.DictReader(stream))
    by_state: dict[str, list[dict[str, str]]] = {}
    for policy in policies:
        by_state.setdefault(policy["State"], []).append(policy)
    unmatched: list[str] = []
    for row in rows:
        expected = normalized(FAIRTEST_NAMES.get(row["school_id"], row["school_name"]))
        candidates = by_state.get(row["state_region"], [])
        scored = [
            (SequenceMatcher(None, expected, normalized(item["Institution Name"])).ratio(), item)
            for item in candidates
        ]
        if not scored:
            unmatched.append(f"{row['school_id']}: missing FairTest record")
            continue
        score, policy = max(scored, key=lambda item: item[0])
        if score < 0.82:
            unmatched.append(f"{row['school_id']}: ambiguous FairTest identity match")
            continue
        normalized_policy = FAIRTEST_POLICY_MAP.get(
            policy["Policy for 2026 - 27 Applicants (enrolling in 2027 -28)"]
        )
        if normalized_policy is None:
            unmatched.append(f"{row['school_id']}: unsupported FairTest policy")
            continue
        row["test_policy_2026_27"] = normalized_policy
        row["test_policy_status"] = "VERIFIED_2026_27_FAIRTEST"
        row["test_policy_source_url"] = (
            clean_source_url(policy["Link to policy"]) if policy["Link to policy"] else FAIRTEST_URL
        )
    return unmatched


def select_match(row: dict[str, str], candidates: list[dict[str, Any]]) -> tuple[dict[str, Any] | None, float]:
    expected_name = normalized(row["school_name"])
    scored: list[tuple[float, dict[str, Any]]] = []
    for candidate in candidates:
        candidate_name = normalized(str(candidate.get("school.name", "")))
        similarity = SequenceMatcher(None, expected_name, candidate_name).ratio()
        if candidate.get("school.state") == row["state_region"]:
            similarity += 0.12
        if normalized(str(candidate.get("school.city", ""))) == normalized(row["city"]):
            similarity += 0.06
        scored.append((similarity, candidate))
    if not scored:
        return None, 0
    score, candidate = max(scored, key=lambda item: item[0])
    return (candidate, score) if score >= 0.82 else (None, score)


def number(value: Any, *, multiplier: int = 1) -> str:
    if value is None or str(value).strip() in {"", "NA", "PrivacySuppressed", "NULL"}:
        return ""
    result = float(value) * multiplier
    return str(round(result, 2)).rstrip("0").rstrip(".")


def summed(candidate: dict[str, Any], first: str, second: str) -> str:
    left, right = candidate.get(first), candidate.get(second)
    if left is None or right is None or str(left) in {"", "NA"} or str(right) in {"", "NA"}:
        return ""
    return str(int(left) + int(right))


def enrich(row: dict[str, str], candidate: dict[str, Any], score: float) -> None:
    row["school_name"] = str(candidate["school.name"])
    row["city"] = str(candidate["school.city"])
    row["state_region"] = str(candidate["school.state"])
    if candidate.get("school.ownership") in OWNERSHIP:
        row["institution_type"] = OWNERSHIP[candidate["school.ownership"]]
    row["acceptance_rate"] = number(
        candidate.get("latest.admissions.admission_rate.overall"), multiplier=100
    )
    row["sat_25"] = summed(
        candidate,
        "latest.admissions.sat_scores.25th_percentile.critical_reading",
        "latest.admissions.sat_scores.25th_percentile.math",
    )
    row["sat_75"] = summed(
        candidate,
        "latest.admissions.sat_scores.75th_percentile.critical_reading",
        "latest.admissions.sat_scores.75th_percentile.math",
    )
    row["act_25"] = number(candidate.get("latest.admissions.act_scores.25th_percentile.cumulative"))
    row["act_75"] = number(candidate.get("latest.admissions.act_scores.75th_percentile.cumulative"))
    tuition = number(candidate.get("latest.cost.tuition.out_of_state"))
    attendance = number(
        candidate.get("latest.cost.attendance.academic_year")
    )
    row["tuition_usd"] = tuition
    row["estimated_cost_of_attendance_usd"] = (
        attendance if not tuition or not attendance or float(attendance) >= float(tuition) else ""
    )
    row["admissions_metrics_status"] = "VERIFIED_LATEST_FEDERAL_SOURCE"
    row["data_as_of"] = DATA_AS_OF
    row["identity_confidence"] = "HIGH" if score >= 1 else "MEDIUM"
    unit_id = candidate["id"]
    row["current_data_reference"] = f"https://collegescorecard.ed.gov/school/?{unit_id}"
    note = (
        "Latest available College Scorecard/IPEDS fields; not represented as 2026-27 outcomes. "
        "SAT bounds sum the corresponding official section percentiles; SAT/ACT medians and "
        "application fee remain blank unless directly sourced."
    )
    row["notes"] = note


def validate(rows: list[dict[str, str]], unmatched: list[str]) -> list[str]:
    issues = list(unmatched)
    if len(rows) != 200:
        issues.append(f"expected 200 rows; found {len(rows)}")
    ids = [row["school_id"] for row in rows]
    if len(ids) != len(set(ids)):
        issues.append("duplicate school_id")
    identities = [(normalized(row["school_name"]), row["state_region"], normalized(row["city"])) for row in rows]
    if len(identities) != len(set(identities)):
        issues.append("duplicate normalized institution identity")
    for row in rows:
        label = row["school_id"]
        for field, low, high in (
            ("acceptance_rate", 0, 100), ("sat_25", 400, 1600), ("sat_50", 400, 1600),
            ("sat_75", 400, 1600), ("act_25", 1, 36), ("act_50", 1, 36), ("act_75", 1, 36),
        ):
            if row[field] and not low <= float(row[field]) <= high:
                issues.append(f"{label}: {field} outside range")
        for prefix in ("sat", "act"):
            values = [row[f"{prefix}_{part}"] for part in (25, 50, 75)]
            present = [float(value) for value in values if value]
            if len(present) > 1 and present != sorted(present):
                issues.append(f"{label}: {prefix.upper()} percentiles out of order")
        if (
            row["tuition_usd"]
            and row["estimated_cost_of_attendance_usd"]
            and float(row["estimated_cost_of_attendance_usd"]) < float(row["tuition_usd"])
        ):
            issues.append(f"{label}: COA below tuition")
        if row["test_policy_2026_27"] not in TEST_POLICIES:
            issues.append(f"{label}: invalid test policy")
        if row["international_aid_policy"] not in AID_POLICIES:
            issues.append(f"{label}: invalid aid policy")
    return issues


def write_report(rows: list[dict[str, str]], issues: list[str], matched: int) -> None:
    test_counts = Counter(row["test_policy_2026_27"] for row in rows)
    aid_counts = Counter(row["international_aid_policy"] for row in rows)
    fully_enriched = sum(all(row[field] for field in NUMERIC_FIELDS) for row in rows)
    missing = len(rows) - fully_enriched
    rates = sum(bool(row["acceptance_rate"]) for row in rows)
    costs = sum(bool(row["tuition_usd"] and row["estimated_cost_of_attendance_usd"]) for row in rows)
    aid_review = sum(row["international_aid_policy"] == "UNKNOWN" for row in rows)
    manual_review = aid_review + len(issues)
    lines = [
        "# Evalio Top 200 enrichment validation", "", f"- Total institutions processed: {len(rows)}",
        f"- Federal identity matches: {matched}", f"- Institutions fully enriched: {fully_enriched}",
        f"- Institutions with missing requested data: {missing}",
        "- Testing policies: " + ", ".join(f"{key}={test_counts[key]}" for key in ("REQUIRED", "OPTIONAL", "FLEXIBLE", "BLIND", "UNKNOWN")),
        "- International aid policies: " + ", ".join(f"{key}={aid_counts[key]}" for key in ("NEED_BLIND", "NEED_AWARE", "NO_NEED_BASED_AID", "UNKNOWN")),
        f"- Records with verified acceptance rate: {rates}",
        f"- Records with verified tuition and COA: {costs}",
        f"- Records requiring manual review: {manual_review}", "",
        "## Manual review", "",
    ]
    if aid_review:
        lines.append(
            f"- {aid_review} institutions retain `UNKNOWN` international-aid policy; filter that "
            "column for institution-by-institution follow-up."
        )
    lines.append(
        f"- {sum(not row['app_fee_usd'] for row in rows)} application fees remain blank because "
        "the federal release does not contain that field."
    )
    lines.append(
        "- SAT/ACT median columns remain blank; the available federal midpoint is derived rather "
        "than an institution-reported median."
    )
    lines += [f"- Automated integrity issue: {issue}" for issue in issues]
    if not issues:
        lines.append("- No duplicate, range, percentile-order, COA, or identity conflicts remain.")
    lines += [
        "", "## Method note", "",
        "Federal values are the latest available College Scorecard/IPEDS observations and are not relabeled as 2026-27 outcomes. Testing policy uses FairTest's 2026-27 database and its linked institution pages. International-aid fields remain `UNKNOWN` unless the input already carried stronger institution-specific evidence. Blank medians and application fees were intentionally not inferred. The original schema has no dedicated field for international first-year acceptance, so that attribute was not added.",
        "", "## Sources", "",
        "1. U.S. Department of Education, [College Scorecard dataset](https://catalog.data.gov/dataset/college-scorecard), May 2025 institution-level release — identity, admissions, testing percentiles, tuition, and annual cost fields.",
        "2. U.S. Department of Education, [College Scorecard institution-level technical documentation](https://collegescorecard.ed.gov/files/InstitutionDataDocumentation.pdf), September 2025 — field definitions and cohort limitations.",
        "3. FairTest, [Overview of Current Admission Testing Policies](https://fairtest.org/test-optional-list/), 2026-27 cycle — normalized required, optional, and test-free policies plus institution policy links.",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=SOURCE)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--scorecard-zip", type=Path, default=DEFAULT_SCORECARD_ZIP)
    parser.add_argument("--fairtest-csv", type=Path, default=DEFAULT_FAIRTEST_CSV)
    args = parser.parse_args()
    with args.input.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)
    fairtest_issues = apply_fairtest(rows, args.fairtest_csv)
    federal_issues: list[str] = []
    scorecard = load_scorecard(args.scorecard_zip)
    by_state: dict[str, list[dict[str, Any]]] = {}
    by_id = {str(candidate["id"]): candidate for candidate in scorecard}
    for candidate in scorecard:
        by_state.setdefault(str(candidate["school.state"]), []).append(candidate)
    for row in rows:
        manual_id = MANUAL_UNIT_IDS.get(row["school_id"])
        if manual_id:
            candidate, score = by_id.get(manual_id), 1.1
        else:
            candidate, score = select_match(row, by_state.get(row["state_region"], []))
        if candidate is None:
            federal_issues.append(f"{row['school_id']}: no confident federal identity match")
            continue
        enrich(row, candidate, score)
    issues = validate(rows, federal_issues + fairtest_issues)
    with args.output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    write_report(rows, issues, len(rows) - len(federal_issues))
    review_count = sum(row["international_aid_policy"] == "UNKNOWN" for row in rows) + len(issues)
    print(f"Wrote {args.output} with {len(rows)} rows; manual review items={review_count}")


if __name__ == "__main__":
    main()
