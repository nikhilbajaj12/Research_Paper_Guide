"""Regression tests for pipeline-blocking integration contracts."""

import json
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, Conference
from app.services.parser_service import ParserService
from app.utils.data_loader import load_conferences_from_json


class RecordingParser:
    """Minimal parser double that records the routed file path."""

    def __init__(self):
        self.file_path = None

    def parse(self, file_path):
        self.file_path = file_path
        return {"parser": self}


@pytest.mark.parametrize(
    ("file_type", "parser_attribute"),
    [
        (".pdf", "pdf_parser"),
        (".docx", "docx_parser"),
        (".zip", "latex_parser"),
        ("PDF", "pdf_parser"),
    ],
)
def test_parser_service_routes_existing_upload_file_types(file_type, parser_attribute):
    service = ParserService.__new__(ParserService)
    service.pdf_parser = RecordingParser()
    service.docx_parser = RecordingParser()
    service.latex_parser = RecordingParser()

    result = service.parse("paper-path", file_type)

    selected_parser = getattr(service, parser_attribute)
    assert result["parser"] is selected_parser
    assert selected_parser.file_path == "paper-path"


def test_conference_loader_uses_canonical_conference_type_and_repairs_existing_row(tmp_path):
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    session.add(
        Conference(
            id="neurips-2025",
            abbr="NeurIPS 2025",
            name="Conference on Neural Information Processing Systems",
            start_date="2025-12-02",
            end_date="2025-12-07",
            submission_deadline="2025-09-30",
            location="San Diego",
            flag="US",
            conference_type="workshop",
            topics=[],
        )
    )
    session.commit()

    conferences_file = tmp_path / "conferences.json"
    conferences_file.write_text(
        json.dumps(
            [
                {
                    "id": "neurips-2025",
                    "abbr": "NeurIPS 2025",
                    "name": "Conference on Neural Information Processing Systems",
                    "start_date": "2025-12-02",
                    "submission_deadline": "2025-09-30",
                    "location": "San Diego",
                    "flag": "US",
                    "conference_type": "academic",
                    "topics": [],
                }
            ]
        ),
        encoding="utf-8",
    )

    loaded = load_conferences_from_json(session, str(conferences_file))

    assert loaded == 0
    assert session.get(Conference, "neurips-2025").conference_type == "academic"


def test_conference_loader_uses_canonical_conference_type_for_new_row(tmp_path):
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()

    conferences_file = tmp_path / "conferences.json"
    conferences_file.write_text(
        json.dumps(
            [
                {
                    "id": "neurips-2025",
                    "abbr": "NeurIPS 2025",
                    "name": "Conference on Neural Information Processing Systems",
                    "start_date": "2025-12-02",
                    "submission_deadline": "2025-09-30",
                    "location": "San Diego",
                    "flag": "US",
                    "conference_type": "academic",
                    "topics": [],
                }
            ]
        ),
        encoding="utf-8",
    )

    loaded = load_conferences_from_json(session, str(conferences_file))

    assert loaded == 1
    assert session.get(Conference, "neurips-2025").conference_type == "academic"
