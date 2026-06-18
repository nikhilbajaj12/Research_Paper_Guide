"""Anonymity Fix Agent - removes author-identifying information."""

import re
from typing import Any, Dict, List, Optional
from .base_fix_agent import BaseFixAgent
from ..schemas.auto_fix_schemas import AgentResult
from ..core import get_logger

logger = get_logger(__name__)


class AnonymityFixAgent(BaseFixAgent):
    """Removes author names, affiliations, acknowledgments,
    and replaces them with anonymous placeholders."""

    @property
    def agent_name(self) -> str:
        return "anonymity_fix"

    def can_handle(self, recommendation: Dict[str, Any]) -> bool:
        cat = recommendation.get("category", "")
        return cat == "anonymity"

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

        if tex_content:
            tex_content, tex_changes = self._fix_latex(tex_content)
            changes.extend(tex_changes)
            parsed_paper = document_editor.replace_source_files(
                parsed_paper, "main.tex", tex_content
            )

        extracted_text = parsed_paper.get("extracted_text", "")
        if extracted_text:
            fixed_text, text_changes = self._fix_extracted_text(extracted_text)
            changes.extend(text_changes)
            parsed_paper["extracted_text"] = fixed_text

        if changes:
            audit_log.log_change(self.agent_name, f"Applied {len(changes)} anonymity fixes", "main.tex")

        return AgentResult(
            agent=self.agent_name,
            success=len(changes) > 0,
            changes_made=changes,
        )

    def _fix_latex(self, content: str) -> tuple:
        """Remove author-identifying LaTeX commands."""
        changes = []
        modified = content

        patterns = [
            (r'\\author\{[^}]*\}', '\\author{Anonymous}'),
            (r'\\institute\{[^}]*\}', '\\institute{Anonymous Institution}'),
            (r'\\affiliation\{[^}]*\}', '\\affiliation{Anonymous Institution}'),
            (r'\\address\{[^}]*\}', '\\address{Anonymous}'),
            (r'\\email\{[^}]*\}', ''),
            (r'\\thanks\{[^}]*\}', ''),
            (r'\\acknowledgments\{[^}]*\}', ''),
            (r'\\acknowledgements\{[^}]*\}', ''),
            (r'\\begin\{acknowledgments\}.*?\\end\{acknowledgments\}', '', re.DOTALL),
            (r'\\begin\{acknowledgements\}.*?\\end\{acknowledgements\}', '', re.DOTALL),
        ]

        for pattern, replacement in patterns:
            flags = re.DOTALL if isinstance(replacement, type(re.DOTALL)) else 0
            if re.search(pattern, modified, flags=flags if flags else 0):
                modified = re.sub(pattern, replacement, modified, flags=flags if flags else 0)
                changes.append(f"Applied: {pattern[:40]}...")

        return modified, changes

    def _fix_extracted_text(self, text: str) -> tuple:
        """Remove email addresses and common identifying patterns."""
        changes = []
        modified = text

        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        emails_found = re.findall(email_pattern, modified)
        if emails_found:
            modified = re.sub(email_pattern, '[email removed]', modified)
            changes.append(f"Removed {len(emails_found)} email address(es)")

        return modified, changes
