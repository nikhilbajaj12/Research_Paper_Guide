"""Base checker class."""

from abc import ABC, abstractmethod
from typing import List
from ..schemas import ComplianceIssue
from ..core import get_logger

logger = get_logger(__name__)


class BaseChecker(ABC):
    """Abstract base class for all compliance checkers."""

    def __init__(self):
        """Initialize checker."""
        self.name = self.__class__.__name__

    @abstractmethod
    async def check(self, paper: dict, guidelines: dict) -> List[ComplianceIssue]:
        """
        Run compliance check.
        
        Args:
            paper: Paper metadata and content
            guidelines: Conference guidelines
            
        Returns:
            List of ComplianceIssue objects found
        """
        pass

    def _create_issue(
        self,
        issue_type: str,
        severity: str,
        title: str,
        description: str,
        guideline_reference: str,
        suggested_fix: str,
        paper_location: str = None,
    ) -> ComplianceIssue:
        """
        Helper to create a ComplianceIssue.
        
        TODO: Implement issue creation with ID generation
        """
        # TODO: Generate unique issue ID
        # TODO: Create ComplianceIssue object
        # TODO: Return issue
        pass
