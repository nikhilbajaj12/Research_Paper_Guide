"""Margin checker."""

from typing import List
from .base_checker import BaseChecker
from ..schemas import ComplianceIssue, ComplianceIssueSeverity, ComplianceIssueType
from ..core import get_logger

logger = get_logger(__name__)


class MarginChecker(BaseChecker):
    """Check page margins compliance."""

    async def check(self, paper: dict, guidelines: dict) -> List[ComplianceIssue]:
        """
        Check if paper has correct margins.
        
        TODO: Implement check
        """
        logger.info(f"Checking margins: top={guidelines.get('margin_top_cm')}, bottom={guidelines.get('margin_bottom_cm')}")
        issues = []
        
        # TODO: Extract margin info from PDF
        # TODO: Compare with guidelines
        # TODO: If violations found, create WARNING issues
        # TODO: Return issues
        
        return issues
