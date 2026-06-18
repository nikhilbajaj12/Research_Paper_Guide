"""Recommendation deduplication utility."""

from typing import List, Dict, Any


def deduplicate_recommendations(
    recommendations: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Remove duplicate recommendations based on issue_id, category, and message.

    Args:
        recommendations: List of recommendation dicts with fields including
                        issue_id, category, and message/issue.

    Returns:
        Deduplicated list preserving first occurrence order.
    """
    seen = set()
    deduped = []

    for rec in recommendations:
        issue_id = _rec_value(rec, "issue_id", "")
        category = _rec_value(rec, "category", "")
        message = _rec_value(rec, "message") or _rec_value(rec, "issue", "")

        key = (issue_id, category, message)
        if key not in seen:
            seen.add(key)
            deduped.append(rec)

    return deduped


def _rec_value(rec, key: str, default=None):
    """Read from either dict or object."""
    if isinstance(rec, dict):
        return rec.get(key, default)
    return getattr(rec, key, default)
