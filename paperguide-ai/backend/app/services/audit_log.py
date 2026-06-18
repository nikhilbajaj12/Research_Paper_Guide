"""Audit log service - tracks all changes made during auto-fix pipeline."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from ..core import get_logger

logger = get_logger(__name__)


class AuditLog:
    """Records every change made during the fix pipeline."""

    def __init__(self):
        self.entries: List[Dict[str, Any]] = []
        self.pipeline_id: Optional[str] = None

    def start_pipeline(self, pipeline_id: str, command: str) -> None:
        self.pipeline_id = pipeline_id
        self.entries.append({
            "timestamp": datetime.utcnow().isoformat(),
            "pipeline_id": pipeline_id,
            "event": "pipeline_started",
            "command": command,
        })

    def log_step(self, step_id: str, agent: str, action: str, status: str, details: str = "") -> None:
        self.entries.append({
            "timestamp": datetime.utcnow().isoformat(),
            "pipeline_id": self.pipeline_id,
            "event": "step_executed",
            "step_id": step_id,
            "agent": agent,
            "action": action,
            "status": status,
            "details": details,
        })

    def log_change(self, agent: str, change: str, file_path: str = "") -> None:
        self.entries.append({
            "timestamp": datetime.utcnow().isoformat(),
            "pipeline_id": self.pipeline_id,
            "event": "change_applied",
            "agent": agent,
            "change": change,
            "file_path": file_path,
        })

    def log_error(self, agent: str, error: str) -> None:
        self.entries.append({
            "timestamp": datetime.utcnow().isoformat(),
            "pipeline_id": self.pipeline_id,
            "event": "error",
            "agent": agent,
            "error": error,
        })

    def log_score_comparison(self, before: int, after: int) -> None:
        self.entries.append({
            "timestamp": datetime.utcnow().isoformat(),
            "pipeline_id": self.pipeline_id,
            "event": "score_comparison",
            "before_score": before,
            "after_score": after,
            "improvement": after - before,
        })

    def complete_pipeline(self, success: bool) -> None:
        self.entries.append({
            "timestamp": datetime.utcnow().isoformat(),
            "pipeline_id": self.pipeline_id,
            "event": "pipeline_completed",
            "success": success,
        })

    def get_entries(self) -> List[Dict[str, Any]]:
        return self.entries

    def get_summary(self) -> Dict[str, Any]:
        changes = [e for e in self.entries if e.get("event") == "change_applied"]
        errors = [e for e in self.entries if e.get("event") == "error"]
        return {
            "total_entries": len(self.entries),
            "total_changes": len(changes),
            "total_errors": len(errors),
            "changes": changes,
            "errors": errors,
        }
