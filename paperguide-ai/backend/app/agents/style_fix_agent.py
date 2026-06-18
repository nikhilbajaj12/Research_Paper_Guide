"""Style Fix Agent - improves grammar, readability, and consistency."""

import re
from typing import Any, Dict, List, Optional
from .base_fix_agent import BaseFixAgent
from ..schemas.auto_fix_schemas import AgentResult
from ..core import get_logger

logger = get_logger(__name__)


class StyleFixAgent(BaseFixAgent):
    """Improves grammar, readability, and consistency.
    Does NOT change research meaning or technical content."""

    @property
    def agent_name(self) -> str:
        return "style_fix"

    def can_handle(self, recommendation: Dict[str, Any]) -> bool:
        return True  # style fixes are always beneficial

    async def execute(
        self,
        parsed_paper: Dict[str, Any],
        recommendations: List[Dict[str, Any]],
        guidelines: Dict[str, Any],
        document_editor: Any,
        audit_log: Any,
    ) -> AgentResult:
        changes = []
        tex_content = parsed_paper.get("main_tex_content", "")
        if not tex_content:
            return AgentResult(agent=self.agent_name, success=False, changes_made=[], error="No LaTeX content")

        fixed, tex_changes = self._fix_style(tex_content)
        changes.extend(tex_changes)

        if tex_changes:
            parsed_paper = document_editor.replace_source_files(parsed_paper, "main.tex", fixed)
            audit_log.log_change(self.agent_name, f"Applied {len(tex_changes)} style improvements", "main.tex")

        return AgentResult(
            agent=self.agent_name,
            success=len(changes) > 0,
            changes_made=changes,
        )

    def _fix_style(self, content: str) -> tuple:
        changes = []

        content = re.sub(r'\bwe we\b', 'we', content)
        content = re.sub(r'\bthe the\b', 'the', content)
        content = re.sub(r'\bis is\b', 'is', content)
        content = re.sub(r'\bare are\b', 'are', content)
        content = re.sub(r'\bhas has\b', 'has', content)
        content = re.sub(r'\bhave have\b', 'have', content)
        content = re.sub(r'\ba a\b', 'a', content)
        content = re.sub(r'\ban an\b', 'an', content)
        content = re.sub(r'\bin in\b', 'in', content)
        content = re.sub(r'\bto to\b', 'to', content)
        content = re.sub(r'\bof of\b', 'of', content)
        content = re.sub(r'\bfor for\b', 'for', content)
        content = re.sub(r'\band and\b', 'and', content)
        content = re.sub(r'\bor or\b', 'or', content)

        content = content.replace(" .", ".")
        content = content.replace(" ,", ",")
        content = content.replace(" ;", ";")
        content = content.replace(" :", ":")
        content = content.replace("( ", "(")
        content = content.replace(" )", ")")
        content = content.replace("[ ", "[")
        content = content.replace(" ]", "]")

        content = re.sub(r'(?<!\n)\n(?!\n)', ' ', content)

        if changes:
            changes.append("Applied basic style improvements (spacing, duplicates, punctuation)")

        return content, changes
