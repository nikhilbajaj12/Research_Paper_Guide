"""Citation checker."""

import re
from typing import List, Dict
from ..core import get_logger

logger = get_logger(__name__)

CITATION_PATTERNS = [
    r'\\cite\{[^}]+\}',
    r'\[[0-9]+\]',
    r'\([A-Z][a-z]+,\s*\d{4}\)',
]


class CitationChecker:
    """Check for citation patterns in paper."""

    def check(self, extracted_text: str, parsed_paper: Dict) -> List[Dict]:
        """Check if paper uses proper citation format."""
        logger.info("Checking for citation patterns")
        issues = []
        
        if not extracted_text:
            return issues
        
        citations_found = False
        for pattern in CITATION_PATTERNS:
            if re.search(pattern, extracted_text):
                citations_found = True
                break
        
        if not citations_found:
            issues.append({
                "issue_id": "no_citations",
                "category": "citations",
                "severity": "warning",
                "message": "No citations detected in paper text.",
                "location": "Throughout paper",
                "suggested_fix": "Add citations using \\cite{}, [1], or (Author, Year) format.",
                "needs_verification": True,
            })
        
        return issues
