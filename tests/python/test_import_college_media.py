from pathlib import Path
from typing import Any
from uuid import UUID

import pytest

import scripts.import_college_media as importer
from scripts.import_college_media import import_media, parse_csv

SEED = Path("data/seed/college_media.csv")


def test_curated_media_seed_has_verified_licensed_rows() -> None:
    rows = parse_csv(SEED)
    assert len(rows) == 3
    assert {row.college_slug for row in rows} == {
        "harvard-university", "massachusetts-institute-of-technology", "stanford-university"
    }
    assert all(row.image_url.startswith("https://commons.wikimedia.org/") for row in rows)
    assert all(row.license and row.alt_text and row.verified_at.tzinfo for row in rows)


def test_media_dry_run_does_not_require_database() -> None:
    rows = parse_csv(SEED)
    assert import_media(rows, dry_run=True) == (3, 0)


def test_media_parser_rejects_unapproved_image_hosts(tmp_path: Path) -> None:
    path = tmp_path / "media.csv"
    path.write_text("college_slug,media_type,image_url,source_url,license,attribution,alt_text,is_primary,width,height,verified_at\nexample,CAMPUS,https://tracker.example/image.jpg,https://example.com/source,CC_BY_4_0,Author,Campus,YES,100,100,2026-09-14T00:00:00+00:00\n", encoding="utf-8")
    with pytest.raises(ValueError, match="not allowlisted"):
        parse_csv(path)


@pytest.mark.parametrize(
    ("is_primary", "verified_at", "message"),
    [
        ("MAYBE", "2026-09-14T00:00:00+00:00", "YES or NO"),
        ("YES", "2026-09-14T00:00:00", "timezone"),
    ],
)
def test_media_parser_rejects_ambiguous_boolean_and_naive_time(
    tmp_path: Path, is_primary: str, verified_at: str, message: str
) -> None:
    path = tmp_path / "media.csv"
    path.write_text(
        "college_slug,media_type,image_url,source_url,license,attribution,alt_text,is_primary,width,height,verified_at\n"
        f"example,CAMPUS,https://commons.wikimedia.org/image.jpg,https://commons.wikimedia.org/source,CC_BY_4_0,Author,Campus,{is_primary},100,100,{verified_at}\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match=message):
        parse_csv(path)


class FakeCursor:
    def __init__(self) -> None:
        self.colleges = {
            "harvard-university": UUID(int=1),
            "massachusetts-institute-of-technology": UUID(int=2),
            "stanford-university": UUID(int=3),
        }
        self.media: set[tuple[UUID, str]] = set()
        self.current: tuple[UUID, str] | None = None

    def __enter__(self) -> "FakeCursor":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def execute(self, statement: str, params: tuple[Any, ...]) -> None:
        if statement.startswith("SELECT id FROM college_media"):
            self.current = (params[0], params[1])
        elif statement.startswith("INSERT INTO college_media"):
            self.media.add((params[1], params[3]))

    def fetchall(self) -> list[tuple[str, UUID]]:
        return list(self.colleges.items())

    def fetchone(self) -> tuple[UUID] | None:
        return (UUID(int=9),) if self.current in self.media else None


class FakeConnection:
    def __init__(self) -> None:
        self.fake_cursor = FakeCursor()

    def __enter__(self) -> "FakeConnection":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def cursor(self) -> FakeCursor:
        return self.fake_cursor


def test_media_upsert_is_idempotent(monkeypatch: pytest.MonkeyPatch) -> None:
    connection = FakeConnection()
    monkeypatch.setattr(importer, "connect_database", lambda _url: connection)
    rows = parse_csv(SEED)

    assert import_media(rows, dry_run=False, database_url="postgresql://example") == (3, 0)
    assert import_media(rows, dry_run=False, database_url="postgresql://example") == (0, 3)
