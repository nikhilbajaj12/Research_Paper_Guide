"""Reference format checker."""

from typing import List
from .base_checker import BaseChecker
from ..schemas import ComplianceIssue, ComplianceIssueSeverity, ComplianceIssueType
from ..core import get_logger

logger = get_logger(__name__)


class ReferenceFormatChecker(BaseChecker):
    """Check citation and reference format compliance."""

    async def check(self, paper: dict, guidelines: dict) -> List[ComplianceIssue]:
        """
        Check if references follow required format (e.g., BibTeX, IEEE, ACM).
        
        TODO: Implement check
        """
        logger.info(f"Checking reference format: required={guidelines.get('reference_format')}")
        issues = []
        
        # TODO: Get required format from guidelines
        # TODO: Parse references from paper
        # TODO: Check each reference for format compliance
        # TODO: If violations found, create WARNING issues
        # TODO: Return issues
        
        return issues
