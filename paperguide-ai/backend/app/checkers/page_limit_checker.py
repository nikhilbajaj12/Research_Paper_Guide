"""Page limit checker."""

from typing import List, Dict
from ..core import get_logger

logger = get_logger(__name__)


class PageLimitChecker:
    """Check if paper exceeds page limit."""

    def check(self, parsed_paper: Dict, guidelines: Dict) -> List[Dict]:
        """Check if paper page count exceeds guideline maximum."""
        logger.info(f"Checking page limit: paper_pages={parsed_paper.get('page_count')}, max={guidelines.get('max_pages')}")
        issues = []
        
        page_count = parsed_paper.get('page_count', 0) or 0
        max_pages = guidelines.get('max_pages', 9) or 9
        
        if page_count > max_pages:
            issues.append({
                "issue_id": "page_limit_exceeded",
                "category": "page_limit",
                "severity": "critical",
                "message": f"Paper exceeds page limit: {page_count} pages vs {max_pages} max.",
                "location": f"Paper page count: {page_count}",
                "suggested_fix": f"Reduce paper to {max_pages} pages or fewer.",
                "needs_verification": False,
            })
        
        return issues
