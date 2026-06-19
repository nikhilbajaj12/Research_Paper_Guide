"""Research integrity validator — combines Reference, Citation, Claims checkers."""

from typing import List
from ..schemas import ParsedDocument, ValidationResult
from ..checkers.reference_checker import ReferenceChecker
from ..checkers.citation_checker import CitationChecker
from ..checkers.claims_checker import ClaimsChecker
from ..core import get_logger
from .base_validator import BaseValidator

logger = get_logger(__name__)


class ResearchIntegrityValidator(BaseValidator):
    """Validate references, citations, and numeric claims integrity."""

    def __init__(self):
        super().__init__()
        self._ref_checker = ReferenceChecker()
        self._citation_checker = CitationChecker()
        self._claims_checker = ClaimsChecker()

    async def validate(self, parsed_doc: ParsedDocument, guidelines: dict) -> List[ValidationResult]:
        logger.info("Validating research integrity (references, citations, claims)")
        results = []

        parsed_doc = self._to_parsed_document(parsed_doc)
        extracted_text = parsed_doc.extracted_text or ""
        parsed_dict = parsed_doc.to_dict()

        ref_issues = self._ref_checker.check(parsed_dict, guidelines)
        for issue in ref_issues:
            results.append(ValidationResult(
                status=issue.get("severity", "warning"),
                issue=issue.get("message", ""),
                location=issue.get("location", ""),
                recommendation=issue.get("suggested_fix", ""),
                category="references",
                needs_verification=issue.get("needs_verification", False),
            ))

        citation_issues = self._citation_checker.check(extracted_text, parsed_dict)
        for issue in citation_issues:
            results.append(ValidationResult(
                status=issue.get("severity", "warning"),
                issue=issue.get("message", ""),
                location=issue.get("location", ""),
                recommendation=issue.get("suggested_fix", ""),
                category="citations",
                needs_verification=issue.get("needs_verification", False),
            ))

        claims_issues = self._claims_checker.check(extracted_text, parsed_dict)
        for issue in claims_issues:
            results.append(ValidationResult(
                status=issue.get("severity", "warning"),
                issue=issue.get("message", ""),
                location=issue.get("location", ""),
                recommendation=issue.get("suggested_fix", ""),
                category="claims_integrity",
                needs_verification=issue.get("needs_verification", False),
            ))

        return results
