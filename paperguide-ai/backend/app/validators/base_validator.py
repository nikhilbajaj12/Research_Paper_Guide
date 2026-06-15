"""Base validator abstract class."""

from abc import ABC, abstractmethod
from typing import List
from ..schemas import ParsedDocument, ValidationResult
from ..core import get_logger

logger = get_logger(__name__)


class BaseValidator(ABC):
    """Abstract base class for all V2 validators."""

    def __init__(self):
        self.name = self.__class__.__name__

    @abstractmethod
    async def validate(self, parsed_doc: ParsedDocument, guidelines: dict) -> List[ValidationResult]:
        """
        Run validation checks against a parsed document.

        Args:
            parsed_doc: Standardized parsed document (parse once).
            guidelines: Conference guideline dict.

        Returns:
            List of ValidationResult objects.
        """
        pass
