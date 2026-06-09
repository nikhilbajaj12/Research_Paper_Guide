"""Reference checker."""

from typing import List, Dict
from ..core import get_logger

logger = get_logger(__name__)


class ReferenceChecker:
    """Check if paper has references section."""

    def check(self, parsed_paper: Dict, guidelines: Dict) -> List[Dict]:
        """Check if paper includes references/bibliography section."""
        logger.info("Checking for references section")
        issues = []
        
        has_references = parsed_paper.get('references_found', False)
        
        if not has_references:
            issues.append({
                "issue_id": "no_references",
                "category": "references",
                "severity": "warning",
                "message": "References section not detected in paper.",
                "location": "End of paper (bibliography/references)",
                "suggested_fix": "Add a References or Bibliography section.",
                "needs_verification": True,
            })
        
        return issues
