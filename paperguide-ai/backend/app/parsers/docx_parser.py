"""DOCX parser for extracting text and structure."""

import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from ..core import get_logger

logger = get_logger(__name__)

CITATION_PATTERNS = [
    r'\\cite\{[^}]+\}',
    r'\[[0-9]+\]',
    r'\([A-Z][a-z]+,\s*\d{4}\)',
]

PERCENTAGE_PATTERN = r'(\d+\.?\d*)\s*%'
DECIMAL_PATTERN = r'\b0\.\d+\b'
SPEEDUP_PATTERN = r'(\d+\.?\d*)\s*x(?:times)?|(\d+\.?\d*)×'
BENCHMARK_KEYWORDS = [
    'accuracy', 'loss', 'perplexity', 'speedup', 'throughput',
    'latency', 'improvement', 'outperforms', 'state-of-the-art',
    'achieves', 'metric', 'benchmark', 'baseline', 'performance'
]


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

    def parse(self, file_path: str) -> Dict[str, Any]:
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
            abstract = self._extract_abstract(text)
            citation_patterns = self._find_citation_patterns(text)
            numeric_claims = self._find_numeric_claims(text)

            return {
                "page_count": None,
                "extracted_text": text,
                "sections": sections,
                "title": self._extract_title(text),
                "abstract": abstract,
                "abstract_found": abstract is not None,
                "references_found": self._find_references(text),
                "citation_patterns_found": len(citation_patterns) > 0,
                "citation_patterns": citation_patterns,
                "numeric_claims": numeric_claims,
                "source_type": "docx",
                "source_files": {
                    "original_paper.docx": Path(file_path).read_bytes(),
                },
                "authors": [],
                "bib_files": [],
                "sty_files": [],
                "main_tex_content": None,
                "has_checklist": False,
            }
        except Exception as e:
            logger.error(f"Error parsing DOCX: {str(e)}")
            return self._fallback_result(str(e))

    def _detect_sections(self, text_parts: List[str]) -> List[str]:
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

    def _extract_title(self, text: str) -> Optional[str]:
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        return lines[0][:200] if lines else None

    def _extract_abstract(self, text: str) -> Optional[str]:
        match = re.search(r'\babstract\b\s*[:\-]?\s*(.+?)(?:\n\s*(?:introduction|keywords)\b)', text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()[:500]
        return None

    def _find_abstract(self, text: str) -> bool:
        return bool(re.search(r'\babstract\b', text, re.IGNORECASE))

    def _find_references(self, text: str) -> bool:
        patterns = [r'\breferences\b', r'\bbibliography\b']
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def _find_citation_patterns(self, text: str) -> List[str]:
        found = []
        for pattern in CITATION_PATTERNS:
            matches = re.findall(pattern, text)
            found.extend(matches)
        return found

    def _find_numeric_claims(self, text: str) -> List[Dict[str, Any]]:
        claims = []
        text_lower = text.lower()

        percentages = re.findall(PERCENTAGE_PATTERN, text)
        for pct in percentages[:10]:
            claims.append({"type": "percentage", "value": f"{pct}%", "severity": "warning"})

        decimals = re.findall(DECIMAL_PATTERN, text)
        for dec in set(decimals):
            idx = text.lower().find(dec)
            if idx >= 0:
                surrounding = text_lower[max(0, idx - 100):min(len(text_lower), idx + 100)]
                if any(kw in surrounding for kw in BENCHMARK_KEYWORDS):
                    claims.append({"type": "metric", "value": dec, "severity": "warning"})

        speedups = re.findall(SPEEDUP_PATTERN, text)
        for sp in speedups[:5]:
            val = sp[0] if sp[0] else sp[1]
            if val:
                claims.append({"type": "speedup", "value": f"{val}x", "severity": "warning"})

        return claims

    def _fallback_result(self, error: str = "python-docx not installed") -> Dict[str, Any]:
        return {
            "page_count": None,
            "extracted_text": None,
            "sections": [],
            "title": None,
            "abstract": None,
            "abstract_found": False,
            "references_found": False,
            "citation_patterns_found": False,
            "citation_patterns": [],
            "numeric_claims": [],
            "source_type": "docx",
            "source_files": {},
            "authors": [],
            "bib_files": [],
            "sty_files": [],
            "main_tex_content": None,
            "has_checklist": False,
            "error": error,
        }
