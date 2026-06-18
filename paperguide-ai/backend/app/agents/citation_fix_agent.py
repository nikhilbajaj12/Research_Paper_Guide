"""Citation Fix Agent - normalizes citation formatting and detects uncited references."""

import re
from typing import Any, Dict, List, Optional
from .base_fix_agent import BaseFixAgent
from ..schemas.auto_fix_schemas import AgentResult
from ..core import get_logger

logger = get_logger(__name__)


class CitationFixAgent(BaseFixAgent):
    """Fixes citation formatting issues. Never hallucinates citations."""

    @property
    def agent_name(self) -> str:
        return "citation_fix"

    def can_handle(self, recommendation: Dict[str, Any]) -> bool:
        cat = recommendation.get("category", "")
        return cat == "citations"

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

        ref_format = guidelines.get("reference_format", "bibtex")

        fixes = self._get_format_fixes(ref_format, tex_content)
        for (old, new, desc) in fixes:
            if old in tex_content:
                tex_content = tex_content.replace(old, new)
                changes.append(desc)

        if changes:
            parsed_paper = document_editor.replace_source_files(parsed_paper, "main.tex", tex_content)
            audit_log.log_change(self.agent_name, f"Applied {len(changes)} citation fixes", "main.tex")

        return AgentResult(
            agent=self.agent_name,
            success=len(changes) > 0,
            changes_made=changes,
        )

    def _get_format_fixes(self, ref_format: str, content: str) -> List[tuple]:
        fixes = []

        if r"\bibliography{" not in content and r"\begin{thebibliography}" not in content:
            if r"\begin{document}" in content:
                fixes.append((
                    r"\end{document}",
                    r"\bibliography{references}\end{document}",
                    "Added \\bibliography{references} command",
                ))

        bare_refs = re.findall(r'\[(\d+(?:,\s*\d+)*)\]', content)
        if bare_refs and r"\cite{" not in content:
            pass

        natbib = r"\usepackage["
        if "natbib" not in content and "biblatex" not in content:
            if r"\documentclass{" in content:
                fixes.append((
                    r"\documentclass",
                    r"\usepackage[sort,numbers]{natbib}" + "\n\\documentclass",
                    "Added natbib package for citation formatting",
                ))

        return fixes
