"""Base class for all fix agents."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from ..schemas.auto_fix_schemas import AgentResult


class BaseFixAgent(ABC):
    """Abstract base for document fix agents."""

    @property
    @abstractmethod
    def agent_name(self) -> str:
        """Human-readable agent name."""
        ...

    @abstractmethod
    async def execute(
        self,
        parsed_paper: Dict[str, Any],
        recommendations: List[Dict[str, Any]],
        guidelines: Dict[str, Any],
        document_editor: Any,
        audit_log: Any,
    ) -> AgentResult:
        """Execute fixes on the parsed document."""
        ...

    def can_handle(self, recommendation: Dict[str, Any]) -> bool:
        """Check if this agent can handle a given recommendation."""
        return False
