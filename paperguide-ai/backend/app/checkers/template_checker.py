"""Template checker."""

from typing import List
from .base_checker import BaseChecker
from ..schemas import ComplianceIssue, ComplianceIssueSeverity, ComplianceIssueType
from ..core import get_logger

logger = get_logger(__name__)


class TemplateChecker(BaseChecker):
    """Check if paper uses required template."""

    async def check(self, paper: dict, guidelines: dict) -> List[ComplianceIssue]:
        """
        Check if paper uses conference template.
        
        TODO: Implement check
        """
        logger.info("Checking template compliance")
        issues = []
        
        # TODO: Look for template markers in LaTeX
        # TODO: Check document class
        # TODO: Check required packages
        # TODO: If violations found, create WARNING or SUGGESTION issues
        # TODO: Return issues
        
        return issues
