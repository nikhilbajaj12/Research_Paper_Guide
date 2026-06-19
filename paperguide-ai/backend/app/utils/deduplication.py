"""Recommendation deduplication utility."""

from typing import List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..schemas import ValidationResult


def deduplicate_validation_results(
    results: List["ValidationResult"],
) -> List["ValidationResult"]:
    """Remove duplicate validation results.

    Deduplicates by (category, issue) key — catches exact and
    near-duplicate validation issues.

    Args:
        results: List of ValidationResult objects.

    Returns:
        Deduplicated list preserving first occurrence order.
    """
    seen_content: set = set()
    deduped: list = []

    for result in results:
        category = (result.category or "").strip().lower()
        issue = (result.issue or "").strip().lower()

        key = (category, issue)
        if key not in seen_content:
            seen_content.add(key)
            deduped.append(result)

    return deduped


def deduplicate_recommendations(
    recommendations: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Remove duplicate recommendations.

    Deduplicates by (category, content) key — catches exact and
    near-duplicate suggestions that differ only in casing / whitespace.
    Different issues within the same category are preserved.

    Args:
        recommendations: List of recommendation dicts.

    Returns:
        Deduplicated list preserving first occurrence order.
    """
    seen_content: set = set()
    deduped: list = []

    for rec in recommendations:
        category = (_rec_value(rec, "category", "") or "").strip().lower()
        content = (
            _rec_value(rec, "suggested_action")
            or _rec_value(rec, "issue")
            or _rec_value(rec, "message")
            or ""
        ).strip().lower()

        key = (category, content)
        if key not in seen_content:
            seen_content.add(key)
            deduped.append(rec)

    return deduped


def _rec_value(rec, key: str, default=None):
    """Read from either dict or object."""
    if isinstance(rec, dict):
        return rec.get(key, default)
    return getattr(rec, key, default)
