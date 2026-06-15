"""LaTeX package generator for Overleaf."""

from typing import Dict, List, Optional
from ..core import get_logger
from .template_engine import TemplateEngine

logger = get_logger(__name__)


class LatexPackageGenerator:
    """Generate LaTeX package for Overleaf."""

    def __init__(self):
        self.template_engine = TemplateEngine()

    def generate_main_tex(
        self,
        parsed_paper: Dict,
        has_citations: bool = False,
        has_references: bool = False,
        conference_config: Optional[Dict] = None,
    ) -> str:
        """Generate main.tex file using conference-aware templates."""
        logger.info("Generating main.tex")

        main_tex_content = parsed_paper.get('main_tex_content')
        if main_tex_content:
            return main_tex_content

        template = (conference_config or {}).get("package_template", "")
        conference_id = (conference_config or {}).get("conference_id", template)

        title = TemplateEngine.escape_latex(
            parsed_paper.get('title') or 'Imported Research Paper'
        )
        abstract = TemplateEngine.escape_latex(
            parsed_paper.get('abstract') or 'Abstract not separately identified during import.'
        )
        body = TemplateEngine.escape_latex(
            parsed_paper.get('extracted_text') or ''
        )

        if has_references:
            bibliography_section = r"\bibliographystyle{plainnat}" + "\n" + r"\bibliography{references}"
        else:
            bibliography_section = r"% TODO: Add \bibliography{} command with your .bib file"

        if has_citations:
            citation_note = r"\nocite{*}"
        else:
            citation_note = r"% TODO: Add \cite{} commands for citations"

        variables = {
            "title": title,
            "abstract": abstract,
            "body": body,
            "bibliography_section": bibliography_section,
            "citation_note": citation_note,
            "style_file": f"{template}_2026" if template else "conference_2026",
            "conference_name": (conference_config or {}).get("conference_name", "Conference"),
        }

        if template:
            try:
                rendered = self.template_engine.render_main_tex(template, variables)
                logger.info(f"Template-based main.tex generated for conference: {template}")
                return rendered
            except FileNotFoundError:
                logger.warning(f"No template for {template}, falling back to default")

        try:
            rendered = self.template_engine.render_main_tex("default", variables)
            logger.info("Default template fallback used for main.tex")
            return rendered
        except FileNotFoundError:
            logger.warning("No default template found, using hardcoded fallback")

        return self._generate_fallback_main_tex(
            title, abstract, body, has_citations, has_references, template
        )

    def _generate_fallback_main_tex(
        self, title: str, abstract: str, body: str,
        has_citations: bool, has_references: bool, template: str
    ) -> str:
        """Hardcoded fallback if no template files exist."""
        style_package = f"\\usepackage{{{template}_2026}}" if template else ""

        tex_content = rf"""\documentclass{{article}}

{style_package}

% TODO: Verify this style file exists in your Overleaf project

\usepackage{{amsmath}}
\usepackage{{amssymb}}
\usepackage{{graphicx}}
\usepackage{{hyperref}}

% Anonymous author block for submission
\author{{Anonymous submission}}

\title{{{title}}}

\begin{{document}}

\maketitle

\begin{{abstract}}
{abstract}
\end{{abstract}}

\section*{{Imported Paper Content}}
{body}

"""

        if has_references:
            tex_content += r"\bibliographystyle{plainnat}" + "\n" + r"\bibliography{references}" + "\n"

        if has_citations:
            tex_content += r"\nocite{*}" + "\n"
        else:
            tex_content += r"% TODO: Add \cite{} commands for citations" + "\n"

        tex_content += r"""
\end{document}
"""
        return tex_content

    @staticmethod
    def generate_references_bib() -> str:
        """Generate references.bib template."""
        logger.info("Generating references.bib")
        
        return """% TODO: Convert reference text to BibTeX format
% Examples:

% @article{Author2024,
%     author = {Author, A. and Coauthor, B.},
%     title = {Paper Title},
%     journal = {Journal Name},
%     year = {2024},
%     volume = {10},
%     pages = {1--10}
% }

% @inproceedings{Conf2024,
%     author = {Person, P.},
%     title = {Conference Paper Title},
%     booktitle = {Proceedings of Conference},
%     year = {2024}
% }

% Add your references above
"""

    def generate_readme(
        self,
        conference_config: Optional[Dict] = None,
        compliance_data: Optional[Dict] = None,
    ) -> str:
        """Generate Overleaf instructions README using conference-aware templates."""
        logger.info("Generating README_OVERLEAF_INSTRUCTIONS.md")

        template = (conference_config or {}).get("package_template", "")
        conference_id = (conference_config or {}).get("conference_id", template)

        style_file = f"{template}_2026" if template else "conference_2026"
        conference_name = (conference_config or {}).get("conference_name", "Conference")

        page_limit = str((conference_config or {}).get("max_pages", "N/A"))
        reference_style = (conference_config or {}).get("reference_format", "bibtex")
        blind_review = "Yes" if (conference_config or {}).get("requires_anonymity", True) else "No"

        compliance_data = compliance_data or {}
        compliance_score = str(compliance_data.get("readiness_score", "N/A"))
        compliance_status = compliance_data.get("overall_status", "unknown")
        critical_count = str(compliance_data.get("critical_count", "N/A"))
        warnings_count = str(compliance_data.get("warnings_count", "N/A"))

        template_urls = {
            "neurips": "https://neurips.cc/Conferences/2026/PaperInformation/StyleFiles",
            "icml": "https://icml.cc/Conferences/2026/StyleFiles",
            "acl": "https://acl-org.github.io/ACL-style-files/",
            "cvpr": "https://cvpr.thecvf.com/Conferences/2026/AuthorGuidelines",
            "emnlp": "https://2026.emnlp.org/call-for-papers/",
        }
        template_url = template_urls.get(template, f"https://{conference_id}.cc/")

        variables = {
            "conference_name": conference_name,
            "conference_id": conference_id,
            "style_file": style_file,
            "template_url": template_url,
            "page_limit": page_limit,
            "reference_style": reference_style,
            "blind_review": blind_review,
            "compliance_score": compliance_score,
            "compliance_status": compliance_status,
            "critical_count": critical_count,
            "warnings_count": warnings_count,
        }

        if template:
            try:
                rendered = self.template_engine.render_readme(template, variables)
                logger.info(f"Template-based README generated for conference: {template}")
                return rendered
            except FileNotFoundError:
                logger.warning(f"No README template for {template}, falling back to default")

        try:
            rendered = self.template_engine.render_readme("default", variables)
            logger.info("Default template fallback used for README")
            return rendered
        except FileNotFoundError:
            logger.warning("No default README template found, using hardcoded fallback")

        return self._generate_fallback_readme()

    @staticmethod
    def _generate_fallback_readme() -> str:
        """Hardcoded fallback README if no template files exist."""
        return """# Overleaf LaTeX Package Instructions

## Setup

1. **Create New Project**: 
   - Go to Overleaf.com
   - Create new project from uploaded ZIP

2. **Verify Template**:
   - Ensure the conference `.sty` file exists in project root
   - If missing, upload or install manually

3. **Set Main File**:
   - In Overleaf menu, set `main.tex` as main file

4. **Add References**:
   - Edit `references.bib` with your BibTeX entries
   - Delete TODO examples
   - Do NOT leave empty references.bib if using citations

## Compilation

1. Recompile from scratch if references do not appear:
   - Delete auxiliary files: `.aux`, `.bbl`, `.log`
   - Recompile main.tex

2. If compilation fails:
   - Check `main.tex` for syntax errors
   - Verify all `\\cite{}` commands have matching entries in `references.bib`
   - Check character encoding (UTF-8)

## Compliance

See `compliance_report.json` for detailed checklist results.
See `recommendations.md` for actionable fix suggestions.
"""

    @staticmethod
    def generate_compliance_report_note(
        readiness_score: int,
        overall_status: str,
        critical_issues: int,
        warnings: int
    ) -> str:
        """Generate compliance note for package."""
        return f"""# Compliance Report Summary

## Score: {readiness_score}/100
## Status: {overall_status}

- Critical Issues: {critical_issues}
- Warnings: {warnings}

See compliance_report.json for full details.
See recommendations.md for actionable fix suggestions.

## Next Steps

1. Review issues in compliance_report.json
2. Address critical issues first
3. Fix warnings as possible
4. Review recommendations in recommendations.md
5. Verify all TODO items in main.tex
6. Test compilation in Overleaf
7. Download and submit

Note: This is an automated compliance check.
Manual review is still required before submission.
"""

    @staticmethod
    def generate_recommendations_md(recommendations: List[Dict]) -> str:
        """Generate recommendations markdown file."""
        if not recommendations:
            return """# Recommendations

No recommendations generated. Your paper passed all compliance checks.

"""

        lines = ["# Recommendations", "", "## Actionable Fix Suggestions", ""]
        for i, rec in enumerate(recommendations, 1):
            issue = rec.get("issue", rec.get("suggested_action", "Unknown issue"))
            category = rec.get("category", "general")
            severity = rec.get("severity", "warning")
            location = rec.get("location", "N/A")
            suggested_action = rec.get("suggested_action", "")
            explanation = rec.get("explanation", "")
            can_auto_fix = rec.get("can_auto_fix", False)

            lines.append(f"### {i}. {issue}")
            lines.append(f"")
            lines.append(f"- **Category**: {category}")
            lines.append(f"- **Severity**: {severity}")
            lines.append(f"- **Location**: {location}")
            lines.append(f"- **Auto-fixable**: {'Yes' if can_auto_fix else 'No'}")
            if suggested_action:
                lines.append(f"- **Suggested Action**: {suggested_action}")
            if explanation:
                lines.append(f"- **Explanation**: {explanation}")
            lines.append("")

        lines.append("---")
        lines.append("")
        lines.append("*Generated by PaperGuide AI compliance analysis*")
        lines.append("")

        return "\n".join(lines)
