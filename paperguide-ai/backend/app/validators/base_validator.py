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

    @staticmethod
    def _to_parsed_document(parsed_doc) -> ParsedDocument:
        """Normalize input: accept both ParsedDocument and plain dict."""
        if isinstance(parsed_doc, ParsedDocument):
            return parsed_doc
        if isinstance(parsed_doc, dict):
            valid_fields = ParsedDocument.__dataclass_fields__.keys()
            filtered = {k: v for k, v in parsed_doc.items() if k in valid_fields}
            filtered.setdefault("paper_id", "")
            filtered.setdefault("file_type", "")
            return ParsedDocument(**filtered)
        return parsed_doc

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
