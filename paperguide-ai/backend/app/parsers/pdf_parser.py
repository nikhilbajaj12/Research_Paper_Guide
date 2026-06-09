"""PDF parser for extracting text and metadata."""

import re
from typing import Optional, List, Dict
from ..core import get_logger

logger = get_logger(__name__)


class PDFParser:
    """Parse PDF files using PyPDF2 or pymupdf."""

    def __init__(self):
        """Initialize parser."""
        try:
            import PyPDF2
            self.PyPDF2 = PyPDF2
            self.available = True
        except ImportError:
            self.PyPDF2 = None
            self.available = False
            logger.warning("PyPDF2 not installed. PDF parsing limited.")

    def parse(self, file_path: str) -> Dict:
        """Extract text, page count, and sections from PDF."""
        if not self.available:
            return self._fallback_result()

        try:
            with open(file_path, 'rb') as f:
                reader = self.PyPDF2.PdfReader(f)
                page_count = len(reader.pages)
                
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            
            sections = self._detect_sections(text)
            
            return {
                "page_count": page_count,
                "extracted_text": text[:5000],
                "sections": sections,
                "abstract_found": self._find_abstract(text),
                "references_found": self._find_references(text),
            }
        except Exception as e:
            logger.error(f"Error parsing PDF: {str(e)}")
            return {
                "page_count": None,
                "extracted_text": None,
                "sections": [],
                "abstract_found": False,
                "references_found": False,
                "error": str(e),
            }

    def _detect_sections(self, text: str) -> List[str]:
        """Detect main sections in text."""
        sections = []
        common_sections = [
            "abstract", "introduction", "method", "results", 
            "experiment", "conclusion", "references", "related work",
            "background", "discussion", "future work"
        ]
        
        text_lower = text.lower()
        for section in common_sections:
            if re.search(rf'\b{section}\b', text_lower):
                sections.append(section)
        
        return sections

    def _find_abstract(self, text: str) -> bool:
        """Check if abstract section exists."""
        return bool(re.search(r'\babstract\b', text, re.IGNORECASE))

    def _find_references(self, text: str) -> bool:
        """Check if references section exists."""
        patterns = [r'\breferences\b', r'\bbibliography\b']
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def _fallback_result(self) -> Dict:
        """Return fallback result when PyPDF2 unavailable."""
        return {
            "page_count": None,
            "extracted_text": None,
            "sections": [],
            "abstract_found": False,
            "references_found": False,
            "error": "PyPDF2 not installed",
        }
        return 0
