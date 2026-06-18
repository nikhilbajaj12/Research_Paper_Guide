"""Reference Fix Agent - normalizes bibliography format to match conference style."""

import re
from typing import Any, Dict, List, Optional
from .base_fix_agent import BaseFixAgent
from ..schemas.auto_fix_schemas import AgentResult
from ..core import get_logger

logger = get_logger(__name__)

STYLE_TEMPLATES = {
    "bibtex": "@article{key,\n  author    = {Author},\n  title     = {Title},\n  journal   = {Journal},\n  year      = {2025},\n}",
    "acm": "@inproceedings{key,\n  author    = {Author},\n  title     = {Title},\n  booktitle = {Proceedings},\n  year      = {2025},\n}",
    "ieee": "@article{key,\n  author  = {Author},\n  title   = {Title},\n  journal = {Journal},\n  year    = {2025},\n  volume  = {},\n  number  = {},\n  pages   = {},\n}",
}


class ReferenceFixAgent(BaseFixAgent):
    """Normalizes bibliography format to match conference requirements."""

    @property
    def agent_name(self) -> str:
        return "reference_fix"

    def can_handle(self, recommendation: Dict[str, Any]) -> bool:
        cat = recommendation.get("category", "")
        return cat == "references"

    async def execute(
        self,
        parsed_paper: Dict[str, Any],
        recommendations: List[Dict[str, Any]],
        guidelines: Dict[str, Any],
        document_editor: Any,
        audit_log: Any,
    ) -> AgentResult:
        changes = []
        ref_style = guidelines.get("reference_format", "bibtex")

        bib_files = parsed_paper.get("bib_files", [])
        tex_content = parsed_paper.get("main_tex_content", "")

        if not bib_files and not tex_content:
            return AgentResult(agent=self.agent_name, success=False, changes_made=[], error="No references found")

        tex_fixes = self._fix_tex_references(tex_content, ref_style)
        for (old, new, desc) in tex_fixes:
            if old in tex_content:
                tex_content = tex_content.replace(old, new)
                changes.append(desc)

        if not bib_files:
            bib_content = STYLE_TEMPLATES.get(ref_style, STYLE_TEMPLATES["bibtex"])
            source_files = parsed_paper.get("source_files", {})
            if "references.bib" not in source_files:
                source_files["references.bib"] = bib_content.encode("utf-8")
                parsed_paper["bib_files"] = ["references.bib"]
                changes.append(f"Created references.bib ({ref_style} format)")
                audit_log.log_change(self.agent_name, "Created references.bib", "references.bib")

        if tex_fixes:
            parsed_paper = document_editor.replace_source_files(parsed_paper, "main.tex", tex_content)
            audit_log.log_change(self.agent_name, f"Applied {len(tex_fixes)} reference fixes", "main.tex")

        return AgentResult(
            agent=self.agent_name,
            success=len(changes) > 0,
            changes_made=changes,
        )

    def _fix_tex_references(self, content: str, ref_style: str) -> List[tuple]:
        fixes = []
        if r"\bibliographystyle{" not in content:
            style_map = {"acm": "acm", "ieee": "ieeetr", "bibtex": "plain"}
            bs = style_map.get(ref_style, "plain")
            if r"\bibliography{" in content:
                fixes.append((
                    r"\bibliography{",
                    rf"\bibliographystyle{{{bs}}}" + "\n" + r"\bibliography{",
                    f"Added \\bibliographystyle{{{bs}}}",
                ))
        return fixes
