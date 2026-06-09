"""Report generator for creating compliance reports."""

import json
from datetime import datetime
from typing import Dict, List, Any
from ..core import get_logger
from ..schemas import ComplianceReport, ComplianceSummary, FixSuggestion, ComplianceIssueDetail

logger = get_logger(__name__)


class ReportGenerator:
    """Generate compliance reports in JSON format."""

    def generate_json_report(self, report_data: Dict[str, Any]) -> str:
        """Generate JSON compliance report."""
        logger.info(f"Generating JSON report for paper: {report_data.get('paper_id')}")
        
        try:
            report_json = json.dumps(report_data, indent=2, default=str)
            return report_json
        except Exception as e:
            logger.error(f"Error generating JSON report: {str(e)}")
            raise

    def save_report_to_file(self, report_json: str, file_path: str) -> None:
        """Save JSON report to file."""
        logger.info(f"Saving report to: {file_path}")
        try:
            with open(file_path, 'w') as f:
                f.write(report_json)
        except Exception as e:
            logger.error(f"Error saving report to file: {str(e)}")
            raise

    def create_report_dict(
        self,
        project_id: str,
        paper_id: str,
        conference_id: str,
        overall_status: str,
        readiness_score: int,
        summary: Dict[str, int],
        issues: List[Dict],
        fix_suggestions: List[Dict],
        passed_checks: List[str],
    ) -> Dict[str, Any]:
        """Create report dictionary."""
        return {
            "project_id": project_id,
            "paper_id": paper_id,
            "conference_id": conference_id,
            "overall_status": overall_status,
            "readiness_score": readiness_score,
            "summary": {
                "total_checks": summary.get("total_checks", 0),
                "passed_count": summary.get("passed_count", 0),
                "warning_count": summary.get("warning_count", 0),
                "critical_count": summary.get("critical_count", 0),
                "info_count": summary.get("info_count", 0),
            },
            "issues": issues,
            "fix_suggestions": fix_suggestions,
            "passed_checks": passed_checks,
            "generated_at": datetime.utcnow().isoformat(),
        }
