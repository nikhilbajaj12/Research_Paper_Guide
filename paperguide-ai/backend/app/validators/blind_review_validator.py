"""Blind review validator — wraps AnonymityChecker."""

from typing import List
from ..schemas import ParsedDocument, ValidationResult
from ..checkers.anonymity_checker import AnonymityChecker
from ..core import get_logger
from .base_validator import BaseValidator

logger = get_logger(__name__)


class BlindReviewValidator(BaseValidator):
    """Check paper for author-identifying information (anonymity)."""

    def __init__(self):
        super().__init__()
        self._checker = AnonymityChecker()

    async def validate(self, parsed_doc: ParsedDocument, guidelines: dict) -> List[ValidationResult]:
        logger.info("Validating blind review (anonymity)")
        results = []

        parsed_doc = self._to_parsed_document(parsed_doc)
        if not guidelines.get("requires_anonymity", False):
            return results

        extracted_text = parsed_doc.extracted_text or ""
        raw_issues = self._checker.check(extracted_text, parsed_doc.to_dict())

        for issue in raw_issues:
            results.append(ValidationResult(
                status=issue.get("severity", "warning"),
                issue=issue.get("message", ""),
                location=issue.get("location", ""),
                recommendation=issue.get("suggested_fix", ""),
                category="anonymity",
                needs_verification=issue.get("needs_verification", False),
            ))

        return results
