"""DOCX parser for extracting text and structure."""

import re
from pathlib import Path
from typing import Dict, List
from ..core import get_logger

logger = get_logger(__name__)


class DOCXParser:
    """Parse DOCX files using python-docx."""

    def __init__(self):
        """Initialize parser."""
        try:
            from docx import Document
            self.Document = Document
            self.available = True
        except ImportError:
            self.Document = None
            self.available = False
            logger.warning("python-docx not installed. DOCX parsing limited.")

    def parse(self, file_path: str) -> Dict:
        """Extract text, paragraphs, and sections from DOCX."""
        if not self.available:
            return self._fallback_result()

        try:
            doc = self.Document(file_path)
            
            text = ""
            headings = []
            
            for para in doc.paragraphs:
                if para.style.name.startswith('Heading'):
                    headings.append(para.text)
                text += para.text + "\n"
            
            sections = self._detect_sections(headings + text.split('\n'))
            
            return {
                "page_count": None,
                "extracted_text": text,
                "sections": sections,
                "abstract_found": self._find_abstract(text),
                "references_found": self._find_references(text),
                "source_type": "docx",
                "source_files": {
                    "original_paper.docx": Path(file_path).read_bytes(),
                },
            }
        except Exception as e:
            logger.error(f"Error parsing DOCX: {str(e)}")
            return {
                "page_count": None,
                "extracted_text": None,
                "sections": [],
                "abstract_found": False,
                "references_found": False,
                "error": str(e),
            }

    def _detect_sections(self, text_parts: List[str]) -> List[str]:
        """Detect main sections from headings and text."""
        sections = []
        common_sections = [
            "abstract", "introduction", "method", "results", 
            "experiment", "conclusion", "references", "related work"
        ]
        
        combined = " ".join(text_parts).lower()
        for section in common_sections:
            if re.search(rf'\b{section}\b', combined):
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
        """Return fallback result when python-docx unavailable."""
        return {
            "page_count": None,
            "extracted_text": None,
            "sections": [],
            "abstract_found": False,
            "references_found": False,
            "error": "python-docx not installed",
        }
