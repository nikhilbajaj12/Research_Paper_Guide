"""Regression tests for compliance accuracy and content-preserving generation."""

import zipfile

import pytest

from app.parsers.latex_zip_parser import LatexZipParser
from app.parsers.pdf_parser import PDFParser
from app.parsers.docx_parser import DOCXParser
from app.routes import compliance, packages
from app.schemas import ComplianceAnalyzeRequest, PackageGenerationRequest
from app.services.latex_package_generator import LatexPackageGenerator
from app.services.package_service import PackageService
from app.core import settings


class GuidelinesStub:
    def __init__(self, max_pages=9, requires_anonymity=True):
        self.max_pages = max_pages
        self.requires_anonymity = requires_anonymity

    def model_dump(self):
        return {
            "max_pages": self.max_pages,
            "requires_anonymity": self.requires_anonymity,
        }


@pytest.mark.asyncio
async def test_compliance_uses_selected_guidelines_and_retains_actual_report(tmp_path, monkeypatch):
    paper_id = "paper-guidelines"
    paper_path = tmp_path / "paper.pdf"
    paper_path.write_bytes(b"pdf")
    compliance.PAPER_STORAGE[paper_id] = {
        "storage_path": str(paper_path),
        "file_type": ".pdf",
        "conference_id": "selected-conference",
    }

    async def get_guidelines(_service, conference_id):
        assert conference_id == "selected-conference"
        return GuidelinesStub(max_pages=1, requires_anonymity=False)

    monkeypatch.setattr(compliance.ConferenceService, "get_guidelines", get_guidelines)
    monkeypatch.setattr(
        compliance.ParserService,
        "parse",
        lambda _service, _path, _type: {
            "page_count": 2,
            "extracted_text": "",
            "references_found": True,
        },
    )

    response = await compliance.analyze_compliance(
        ComplianceAnalyzeRequest(
            paper_id=paper_id,
            conference_id="selected-conference",
        ),
        db=object(),
    )

    assert any(issue.category == "page_limit" for issue in response.issues)
    assert "anonymity" in response.passed_checks
    assert compliance.COMPLIANCE_REPORT_STORAGE[paper_id]["readiness_score"] == response.readiness_score


@pytest.mark.asyncio
async def test_package_generation_uses_retained_compliance_report(tmp_path, monkeypatch):
    paper_id = "paper-report"
    paper_path = tmp_path / "paper.pdf"
    paper_path.write_bytes(b"pdf")
    report = {
        "paper_id": paper_id,
        "conference_id": "selected-conference",
        "readiness_score": 42,
        "overall_status": "not_ready",
        "critical_count": 2,
        "warnings_count": 3,
        "issues": [],
        "passed_checks": [],
    }
    compliance.PAPER_STORAGE[paper_id] = {
        "storage_path": str(paper_path),
        "file_type": ".pdf",
        "conference_id": "selected-conference",
    }
    compliance.COMPLIANCE_REPORT_STORAGE[paper_id] = report
    monkeypatch.setattr(packages.ParserService, "parse", lambda _service, _path, _type: {})

    captured = {}

    def generate_package(**kwargs):
        captured.update(kwargs)
        return "package-id", {
            "zip_file_path": "package.zip",
            "generated_files": [],
            "status": "completed",
            "message": "Package generated successfully",
        }

    monkeypatch.setattr(packages.package_service, "generate_package", generate_package)

    await packages.generate_package(
        PackageGenerationRequest(
            paper_id=paper_id,
            conference_id="selected-conference",
        ),
        db=object(),
    )

    assert captured["compliance_report"] is report
    assert captured["compliance_report"]["readiness_score"] == 42


def test_latex_zip_parser_reads_all_text_and_preserves_project_files(tmp_path):
    zip_path = tmp_path / "paper.zip"
    trailing_claim = "A" * 6000 + " final-section-content"
    figure_bytes = b"\x89PNG\r\n"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("main.tex", r"\documentclass{article}\input{sections/results}")
        archive.writestr("sections/results.tex", trailing_claim)
        archive.writestr("figures/result.png", figure_bytes)
        archive.writestr("references.bib", "@article{example}")

    parsed = LatexZipParser().parse(str(zip_path))

    assert "final-section-content" in parsed["extracted_text"]
    assert set(parsed["tex_files"]) == {"main.tex", "sections/results.tex"}
    assert parsed["source_files"]["figures/result.png"] == figure_bytes
    assert parsed["main_tex_content"].startswith(r"\documentclass")


def test_pdf_parser_keeps_text_after_first_5000_characters(tmp_path):
    class Page:
        def extract_text(self):
            return "A" * 6000 + " final-pdf-content"

    class Reader:
        def __init__(self, _file):
            self.pages = [Page()]

    parser = PDFParser.__new__(PDFParser)
    parser.available = True
    parser.PyPDF2 = type("PyPDF2Stub", (), {"PdfReader": Reader})
    pdf_path = tmp_path / "paper.pdf"
    pdf_path.write_bytes(b"pdf")

    parsed = parser.parse(str(pdf_path))

    assert "final-pdf-content" in parsed["extracted_text"]


def test_docx_parser_keeps_text_after_first_5000_characters(tmp_path):
    class Style:
        name = "Normal"

    class Paragraph:
        style = Style()
        text = "A" * 6000 + " final-docx-content"

    class Document:
        paragraphs = [Paragraph()]

    parser = DOCXParser.__new__(DOCXParser)
    parser.available = True
    parser.Document = lambda _path: Document()
    docx_path = tmp_path / "paper.docx"
    docx_path.write_bytes(b"docx")

    parsed = parser.parse(str(docx_path))

    assert "final-docx-content" in parsed["extracted_text"]


def test_plain_text_package_generation_keeps_and_escapes_paper_content():
    tex = LatexPackageGenerator.generate_main_tex(
        {
            "source_type": "pdf",
            "extracted_text": "Measured accuracy is 91.7% on data_set.",
        }
    )

    assert "Measured accuracy is 91.7\\% on data\\_set." in tex
    assert "Imported Paper Content" in tex


def test_latex_package_generation_keeps_original_main_tex():
    original = r"\documentclass{article}\begin{document}Original body\end{document}"

    tex = LatexPackageGenerator.generate_main_tex(
        {
            "source_type": "latex",
            "main_tex_content": original,
            "extracted_text": "other files",
        }
    )

    assert tex == original


def test_package_service_preserves_source_files_and_actual_report(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "PACKAGE_DIR", str(tmp_path))
    report = {
        "paper_id": "paper",
        "conference_id": "conference",
        "readiness_score": 37,
        "overall_status": "not_ready",
        "critical_count": 2,
        "warnings_count": 4,
    }
    parsed_paper = {
        "main_tex_content": r"\documentclass{article}\begin{document}Body\end{document}",
        "source_files": {
            "main.tex": b"original main",
            "figures/result.png": b"figure-bytes",
            "references.bib": b"@article{example}",
        },
        "bib_files": ["references.bib"],
        "references_found": True,
    }

    _, metadata = PackageService().generate_package(
        paper_id="paper",
        conference_id="conference",
        parsed_paper=parsed_paper,
        compliance_report=report,
    )

    with zipfile.ZipFile(metadata["zip_file_path"]) as archive:
        assert archive.read("figures/result.png") == b"figure-bytes"
        packaged_report = archive.read("compliance_report.json").decode("utf-8")
        assert '"readiness_score": 37' in packaged_report
