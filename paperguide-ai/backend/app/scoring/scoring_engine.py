"""Scoring engine — computes readiness score and status from validation results."""

from typing import List
from ..schemas import ValidationResult, ScoreResult
from ..core import get_logger

logger = get_logger(__name__)

SEVERITY_PENALTIES = {
    "critical": 20,
    "warning": 8,
    "suggestion": 2,
    "info": 2,
}


class ScoringEngine:
    """Deterministic scoring engine for compliance validation results.

    Scoring rules are defined as class attributes for easy configuration.
    """

    def __init__(self):
        self.penalties = dict(SEVERITY_PENALTIES)
        self.max_score = 100
        self.min_score = 0

    def compute(self, results: List[ValidationResult]) -> ScoreResult:
        """Compute score and status from a list of ValidationResult objects."""
        critical_count = 0
        warnings_count = 0
        info_count = 0

        for r in results:
            penalty = self.penalties.get(r.status, 0)
            if r.status == "critical":
                critical_count += 1
            elif r.status == "warning":
                warnings_count += 1
            else:
                info_count += 1

        deduction = (
            critical_count * self.penalties["critical"]
            + warnings_count * self.penalties["warning"]
            + info_count * self.penalties["info"]
        )
        score = max(self.min_score, min(self.max_score, self.max_score - deduction))

        status = self._determine_status(score, critical_count)

        return ScoreResult(
            score=score,
            status=status,
            critical_count=critical_count,
            warnings_count=warnings_count,
            info_count=info_count,
        )

    def _determine_status(self, score: int, critical_count: int) -> str:
        if score >= 90 and critical_count == 0:
            return "submission_ready"
        elif score >= 75 and critical_count == 0:
            return "minor_fixes"
        elif score >= 50:
            return "major_fixes"
        else:
            return "not_ready"
