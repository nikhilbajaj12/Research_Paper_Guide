"""Parser service for routing file parsing."""

import os
from typing import Dict
from ..parsers.pdf_parser import PDFParser
from ..parsers.docx_parser import DOCXParser
from ..parsers.latex_zip_parser import LatexZipParser
from ..schemas import ParsedDocument
from ..core import get_logger

logger = get_logger(__name__)


class ParserService:
    """Service to parse different file types."""

    def __init__(self):
        """Initialize parsers."""
        self.pdf_parser = PDFParser()
        self.docx_parser = DOCXParser()
        self.latex_parser = LatexZipParser()

    def parse(self, file_path: str, file_type: str, paper_id: str) -> ParsedDocument:
        """Parse file based on type and return a ParsedDocument."""
        logger.info(f"Parsing file: {file_path}, type: {file_type}")

        normalized_file_type = file_type.lower().lstrip('.')

        if normalized_file_type == 'pdf':
            raw = self.pdf_parser.parse(file_path)
        elif normalized_file_type == 'docx':
            raw = self.docx_parser.parse(file_path)
        elif normalized_file_type == 'zip':
            raw = self.latex_parser.parse(file_path)
        else:
            logger.warning(f"Unsupported file type: {file_type}")
            return ParsedDocument(
                paper_id=paper_id,
                file_type=file_type,
                error=f"Unsupported file type: {file_type}",
            )

        return ParsedDocument(
            paper_id=paper_id,
            file_type=normalized_file_type,
            title=raw.get("title"),
            abstract=raw.get("abstract"),
            authors=raw.get("authors", []),
            sections=raw.get("sections", []),
            page_count=raw.get("page_count"),
            references_found=raw.get("references_found", False),
            citation_patterns_found=raw.get("citation_patterns_found", False),
            citation_patterns=raw.get("citation_patterns", []),
            numeric_claims=raw.get("numeric_claims", []),
            extracted_text=raw.get("extracted_text"),
            source_files=raw.get("source_files", {}),
            main_tex_content=raw.get("main_tex_content"),
            bib_files=raw.get("bib_files", []),
            sty_files=raw.get("sty_files", []),
            abstract_found=raw.get("abstract_found", False),
            has_checklist=raw.get("has_checklist", False),
            error=raw.get("error"),
        )
