"""Missing section checker."""

from typing import List
from .base_checker import BaseChecker
from ..schemas import ComplianceIssue, ComplianceIssueSeverity, ComplianceIssueType
from ..core import get_logger

logger = get_logger(__name__)


class SectionChecker(BaseChecker):
    """Check for required paper sections."""

    async def check(self, paper: dict, guidelines: dict) -> List[ComplianceIssue]:
        """
        Check if paper has all required sections.
        
        TODO: Implement check
        """
        logger.info("Checking for required sections")
        issues = []
        
        # TODO: Get required sections from guidelines
        # TODO: Get paper structure from metadata
        # TODO: Compare sections
        # TODO: If sections missing, create WARNING issues
        # TODO: Return issues
        
        return issues
