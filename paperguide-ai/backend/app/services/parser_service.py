"""Parser service for routing file parsing."""

import os
from typing import Dict
from ..parsers.pdf_parser import PDFParser
from ..parsers.docx_parser import DOCXParser
from ..parsers.latex_zip_parser import LatexZipParser
from ..core import get_logger

logger = get_logger(__name__)


class ParserService:
    """Service to parse different file types."""

    def __init__(self):
        """Initialize parsers."""
        self.pdf_parser = PDFParser()
        self.docx_parser = DOCXParser()
        self.latex_parser = LatexZipParser()

    def parse(self, file_path: str, file_type: str) -> Dict:
        """Parse file based on type."""
        logger.info(f"Parsing file: {file_path}, type: {file_type}")

        normalized_file_type = file_type.lower().lstrip('.')

        if normalized_file_type == 'pdf':
            return self.pdf_parser.parse(file_path)
        elif normalized_file_type == 'docx':
            return self.docx_parser.parse(file_path)
        elif normalized_file_type == 'zip':
            return self.latex_parser.parse(file_path)
        else:
            logger.warning(f"Unsupported file type: {file_type}")
            return {
                "error": f"Unsupported file type: {file_type}",
                "needs_verification": True,
            }
