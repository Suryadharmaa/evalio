from datetime import UTC, datetime
from pathlib import Path

import pytest

from scripts import college_import


def stage(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, body: str) -> str:
    monkeypatch.setattr(college_import, "STAGING_ROOT", tmp_path / "staging")
    source = tmp_path / "colleges.csv"
    source.write_text(body, encoding="utf-8")
    year = datetime.now(UTC).year
    return college_import.import_rows(source, f"{year}-{(year + 1) % 100:02d}")


def test_invalid_rate_and_percentile_order_are_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run_id = stage(
        tmp_path,
        monkeypatch,
        "name,slug,country_code,source_url,acceptance_rate,sat_25,sat_50,sat_75\nExample,example,US,https://example.edu,2,1500,1400,1300\n",
    )
    result = college_import.validate(run_id)
    assert result["status"] == "REJECTED"
    assert {item["error"] for item in result["validation_errors"]} == {
        "invalid_admit_rate",
        "invalid_sat_percentile_order",
    }


def test_duplicate_and_missing_source_are_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run_id = stage(
        tmp_path,
        monkeypatch,
        "name,slug,country_code,source_url\nOne,same,US,https://one.edu\nTwo,same,US,\n",
    )
    result = college_import.validate(run_id)
    assert result["status"] == "REJECTED"
    assert result["rows_rejected"] == 1


def test_promotion_requires_validation_approval_and_confirmation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run_id = stage(
        tmp_path,
        monkeypatch,
        "name,slug,country_code,source_url\nExample,example,US,https://example.edu\n",
    )
    with pytest.raises(ValueError):
        college_import.promote(run_id, "PROMOTE")
    assert college_import.validate(run_id)["status"] == "VALID"
    with pytest.raises(ValueError):
        college_import.approve(run_id, "wrong")
    assert college_import.approve(run_id, "APPROVE")["status"] == "APPROVED"
    with pytest.raises(ValueError):
        college_import.promote(run_id, "wrong")


def test_dangerous_url_scheme_is_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    run_id = stage(
        tmp_path,
        monkeypatch,
        "name,slug,country_code,source_url\nExample,example,US,javascript:alert(1)\n",
    )
    result = college_import.validate(run_id)
    assert result["validation_errors"][0]["error"] == "invalid_source_url"


def test_source_url_with_credentials_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run_id = stage(
        tmp_path,
        monkeypatch,
        "name,slug,country_code,source_url\n"
        "Example,example,US,https://user:secret@example.edu\n",
    )
    result = college_import.validate(run_id)
    assert result["validation_errors"][0]["error"] == "invalid_source_url"


def test_unknown_enum_bad_slug_and_malformed_numbers_are_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run_id = stage(
        tmp_path,
        monkeypatch,
        "name,slug,country_code,source_url,test_policy,acceptance_rate,sat_25,sat_50,sat_75\n"
        "Example,bad/slug,USA,https://example.edu,SURPRISE,nope,low,mid,high\n",
    )
    errors = {item["error"] for item in college_import.validate(run_id)["validation_errors"]}
    assert {
        "invalid_slug",
        "invalid_country_code",
        "unknown_test_policy",
        "invalid_admit_rate",
        "invalid_sat_percentile_order",
    } <= errors


def test_staging_run_id_cannot_escape_staging_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(college_import, "STAGING_ROOT", tmp_path / "staging")
    with pytest.raises(ValueError, match="run ID"):
        college_import.load_run("../../private")


def test_stale_cycle_rejects_the_full_import(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(college_import, "STAGING_ROOT", tmp_path / "staging")
    source = tmp_path / "colleges.csv"
    source.write_text(
        "name,slug,country_code,source_url\nExample,example,US,https://example.edu\n",
        encoding="utf-8",
    )
    run_id = college_import.import_rows(source, "2020-21")

    result = college_import.validate(run_id)
    assert result["status"] == "REJECTED"
    assert result["rows_valid"] == 0
    assert result["validation_errors"][0]["error"] == "stale_academic_cycle"
