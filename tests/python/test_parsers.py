import io
import zipfile

import pymupdf
import pytest
from docx import Document

from api.admission_engine.parsers.documents import (
    MAX_UPLOAD_BYTES,
    FileTooLargeError,
    NoExtractableTextError,
    UnsupportedFileError,
    parse_document,
)


def test_rejects_extension_content_mismatch_and_oversize() -> None:
    with pytest.raises(UnsupportedFileError):
        parse_document("fake.pdf", b"plain text")
    with pytest.raises(UnsupportedFileError):
        parse_document("fake.docx", b"plain text")
    with pytest.raises(UnsupportedFileError):
        parse_document("binary.txt", b"hello\x00world")
    with pytest.raises(FileTooLargeError):
        parse_document("large.txt", b"x" * (MAX_UPLOAD_BYTES + 1))


def test_extracts_txt_docx_and_pdf_without_temp_files() -> None:
    assert parse_document("../../note.txt", b"hello").text == "hello"
    document = Document()
    document.add_paragraph("DOCX evidence")
    stream = io.BytesIO()
    document.save(stream)
    assert "DOCX evidence" in parse_document("note.docx", stream.getvalue()).text
    pdf = pymupdf.open()  # type: ignore[no-untyped-call]
    page = pdf.new_page()
    page.insert_text((72, 72), "PDF evidence")
    pdf_bytes = pdf.tobytes()  # type: ignore[no-untyped-call]
    pdf.close()  # type: ignore[no-untyped-call]
    assert "PDF evidence" in parse_document("note.pdf", pdf_bytes).text


def test_empty_and_large_csv_are_rejected() -> None:
    with pytest.raises(NoExtractableTextError):
        parse_document("empty.txt", b"  ")
    with pytest.raises(UnsupportedFileError):
        parse_document("rows.csv", ("a\n" * 5_001).encode())


def test_rejects_excessive_extracted_text_and_docx_expansion() -> None:
    with pytest.raises(FileTooLargeError):
        parse_document("large.txt", b"x" * 100_001)

    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as document:
        document.writestr("[Content_Types].xml", "<Types />")
        document.writestr("word/document.xml", "x" * (5 * 1024 * 1024 + 1))
    with pytest.raises(UnsupportedFileError, match="content is too large"):
        parse_document("expanded.docx", archive.getvalue())


def test_scanned_and_encrypted_pdfs_are_rejected() -> None:
    blank = pymupdf.open()  # type: ignore[no-untyped-call]
    blank.new_page()
    blank_bytes = blank.tobytes()  # type: ignore[no-untyped-call]
    blank.close()  # type: ignore[no-untyped-call]
    with pytest.raises(NoExtractableTextError):
        parse_document("scan.pdf", blank_bytes)

    encrypted = pymupdf.open()  # type: ignore[no-untyped-call]
    encrypted.new_page().insert_text((72, 72), "private")
    encrypted_bytes = encrypted.tobytes(  # type: ignore[no-untyped-call]
        encryption=pymupdf.PDF_ENCRYPT_AES_256,  # type: ignore[attr-defined]
        owner_pw="owner-secret",
        user_pw="user-secret",
    )
    encrypted.close()  # type: ignore[no-untyped-call]
    with pytest.raises(UnsupportedFileError):
        parse_document("encrypted.pdf", encrypted_bytes)
