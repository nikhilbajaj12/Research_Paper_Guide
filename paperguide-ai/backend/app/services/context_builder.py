"""AI Assistant context builder - builds context from compliance results."""

from typing import Any, Dict, List, Optional


class ContextBuilder:
    """Build assistant context from compliance analysis results."""

    def build(
        self,
        conference: Optional[Dict[str, Any]] = None,
        compliance_score: int = 0,
        critical_issues: Optional[List[Dict[str, Any]]] = None,
        warnings: Optional[List[Dict[str, Any]]] = None,
        passed_checks: Optional[List[str]] = None,
        recommendations: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Build structured context for the AI assistant."""
        return {
            "conference": conference or {},
            "compliance_score": compliance_score,
            "critical_issues": critical_issues or [],
            "warnings": warnings or [],
            "passed_checks": passed_checks or [],
            "recommendations": recommendations or [],
        }
