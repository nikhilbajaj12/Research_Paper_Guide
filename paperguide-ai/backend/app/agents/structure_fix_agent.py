"""Structure Fix Agent - adds missing required sections."""

import re
from typing import Any, Dict, List, Optional
from .base_fix_agent import BaseFixAgent
from ..schemas.auto_fix_schemas import AgentResult
from ..core import get_logger

logger = get_logger(__name__)


SECTION_TEMPLATES = {
    "abstract": "\\begin{abstract}\nThis section presents the core methodology and approach of our work. "
                "We describe the key innovations and contributions that address the problem identified in the introduction. "
                "The experimental evaluation demonstrates the effectiveness of our proposed approach.\n\\end{abstract}",
    "introduction": "\\section{Introduction}\n\n"
                    "This paper addresses the problem of [task/problem domain]. "
                    "Recent advances in [related area] have shown promising results, "
                    "but existing approaches face limitations in [specific challenge]. "
                    "In this work, we propose a novel method that [key contribution]. "
                    "Our approach achieves [main result] on [benchmark/dataset]. "
                    "The main contributions of this paper are: "
                    "(1) [contribution 1], (2) [contribution 2], and (3) [contribution 3].",
    "related work": "\\section{Related Work}\n\n"
                     "Previous work in this area has explored various approaches. "
                     "[Author et al.] proposed [method] which achieves [result]. "
                     "Similarly, [Author et al.] introduced [approach] for [task]. "
                     "Our work differs from these approaches by [key difference]. "
                     "Unlike prior methods, our technique [novel aspect].",
    "method": "\\section{Method}\n\n"
              "We present our approach for addressing the problem described in Section~\\ref{sec:introduction}. "
              "Our method consists of several key components that work together to achieve the desired outcome.\n\n"
              "\\subsection{Problem Formulation}\n"
              "We formalize the problem as follows. Given [input], the goal is to produce [output]. "
              "Let $X$ denote the input space and $Y$ the output space. "
              "We aim to learn a function $f: X \\rightarrow Y$ that minimizes [objective].\n\n"
              "\\subsection{Proposed Approach}\n"
              "Our approach builds upon [foundation] with several key innovations. "
              "First, we introduce [component 1] which handles [functionality]. "
              "Second, we design [component 2] to address [challenge]. "
              "The overall architecture is illustrated in Figure~\\ref{fig:architecture}.",
    "experiments": "\\section{Experiments}\n\n"
                   "We conduct comprehensive experiments to evaluate the proposed approach. "
                   "Our experimental setup includes multiple datasets and baselines for thorough comparison.\n\n"
                   "\\subsection{Setup}\n"
                   "We implement our method using [framework/language]. "
                   "All experiments are conducted on [hardware] with [software environment]. "
                   "We use [dataset] for training and [dataset] for evaluation.\n\n"
                   "\\subsection{Results}\n"
                   "Table~\\ref{tab:results} presents the main results. "
                   "Our method achieves competitive performance across all benchmarks.",
    "results": "\\section{Results}\n\n"
               "This section presents the experimental results of our proposed approach. "
               "We compare against several state-of-the-art baselines on standard benchmarks.\n\n"
               "\\subsection{Main Results}\n"
               "Our method outperforms existing approaches on the primary evaluation metrics. "
               "Specifically, we achieve [metric] of [value] compared to [baseline value] for the baseline.\n\n"
               "\\subsection{Ablation Studies}\n"
               "We conduct ablation studies to understand the contribution of each component. "
               "Removing [component] leads to a drop of [amount], confirming its importance.",
    "conclusion": "\\section{Conclusion}\n\n"
                  "In this paper, we presented [method name], a novel approach for [task]. "
                  "Our method achieves [main result] on [benchmark], demonstrating its effectiveness. "
                  "Key contributions include [summary of contributions]. "
                  "Future work includes [future directions].",
    "discussion": "\\section{Discussion}\n\n"
                  "We discuss the implications of our findings and limitations of the current approach. "
                  "Our results suggest that [insight]. "
                  "However, there are several limitations that warrant further investigation. "
                  "First, [limitation 1]. Second, [limitation 2]. "
                  "Addressing these limitations presents promising directions for future research.",
}


class StructureFixAgent(BaseFixAgent):
    """Detects and adds missing required sections."""

    @property
    def agent_name(self) -> str:
        return "structure_fix"

    def can_handle(self, recommendation: Dict[str, Any]) -> bool:
        cat = recommendation.get("category", "")
        return cat == "missing_section"

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
            return AgentResult(
                agent=self.agent_name,
                success=False,
                changes_made=[],
                error="No LaTeX content found",
            )

        existing_sections = self._extract_sections(tex_content)
        missing = self._find_missing(
            existing_sections,
            recommendations,
            guidelines.get("required_sections", []),
        )

        tex_content = self._remove_bibliography_todo(tex_content)

        for section_name, template in missing:
            insert_point = self._find_insert_point(tex_content, section_name)
            tex_content = tex_content[:insert_point] + "\n" + template + "\n" + tex_content[insert_point:]
            changes.append(f"Added '{section_name}' section")

        if changes:
            parsed_paper = document_editor.replace_source_files(
                parsed_paper, "main.tex", tex_content
            )
            audit_log.log_change(self.agent_name, f"Added {len(changes)} missing sections", "main.tex")

        return AgentResult(
            agent=self.agent_name,
            success=len(changes) > 0,
            changes_made=changes,
        )

    def _extract_sections(self, content: str) -> List[str]:
        found = re.findall(r'\\(?:section|subsection)\*?\{(.+?)\}', content)
        return [s.strip().lower() for s in found]

    def _find_missing(
        self,
        existing: List[str],
        recommendations: List[Dict[str, Any]],
        required: List[str],
    ) -> List[tuple]:
        missing = []
        needed = set()

        for rec in recommendations:
            msg = rec.get("issue", "").lower()
            for sec_name in SECTION_TEMPLATES:
                if sec_name in msg and sec_name not in existing and sec_name not in needed:
                    needed.add(sec_name)
                    missing.append((sec_name, SECTION_TEMPLATES[sec_name]))

        for req in required:
            r = req.lower()
            if r not in existing and r not in needed and r in SECTION_TEMPLATES:
                needed.add(r)
                missing.append((r, SECTION_TEMPLATES[r]))

        return missing

    def _find_insert_point(self, content: str, section_name: str) -> int:
        doc_end = content.rfind("\\end{document}")
        if doc_end != -1:
            return doc_end

        for marker in ["\\bibliography", "\\begin{references}", "\\end{abstract}"]:
            idx = content.find(marker)
            if idx != -1:
                line_end = content.find("\n", idx)
                if line_end != -1:
                    return line_end + 1
        return len(content)

    def _remove_bibliography_todo(self, content: str) -> str:
        return content.replace(
            "% TODO: Add \\bibliography{} command with your .bib file\n", ""
        ).replace(
            "% TODO: Add \\cite{} commands for citations\n", ""
        )
