"""Anonymity checker."""

from typing import List, Dict
import re
from ..core import get_logger

logger = get_logger(__name__)

EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
AUTHOR_MARKERS = [
    'author', 'affiliation', 'acknowledgement', 'acknowledgment',
    'company', 'organization', 'department', 'university', 'institute', 'lab'
]


class AnonymityChecker:
    """Check for author names, emails, and identifying information."""

    def check(self, extracted_text: str, parsed_paper: Dict) -> List[Dict]:
        """Check if paper contains identifying information."""
        logger.info("Checking for anonymity violations")
        issues = []
        
        if not extracted_text:
            return issues
        
        text_lower = extracted_text.lower()
        
        emails = re.findall(EMAIL_PATTERN, extracted_text)
        if emails:
            for email in emails:
                issues.append({
                    "issue_id": f"anonymity_email_{len(issues)}",
                    "category": "anonymity",
                    "severity": "critical",
                    "message": f"Email address found: {email}. Remove for anonymity.",
                    "location": f"Email: {email}",
                    "suggested_fix": "Remove all email addresses and contact information.",
                    "needs_verification": False,
                })
        
        for marker in AUTHOR_MARKERS:
            if marker in text_lower:
                pattern = rf'\b{marker}\b'
                matches = re.finditer(pattern, text_lower)
                for match in matches:
                    start = max(0, match.start() - 30)
                    end = min(len(extracted_text), match.end() + 30)
                    context = extracted_text[start:end].replace('\n', ' ')[:100]
                    
                    issues.append({
                        "issue_id": f"anonymity_marker_{marker}_{len(issues)}",
                        "category": "anonymity",
                        "severity": "warning" if marker != "author" else "critical",
                        "message": f"Potential author reference '{marker}' detected.",
                        "location": f"Context: {context}",
                        "suggested_fix": f"Review and remove '{marker}' references.",
                        "needs_verification": True,
                    })
        
        return issues
