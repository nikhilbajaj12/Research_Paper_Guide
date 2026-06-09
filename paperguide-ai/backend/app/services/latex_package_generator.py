"""LaTeX package generator for Overleaf."""

import re
from typing import Dict, Optional
from ..core import get_logger

logger = get_logger(__name__)


class LatexPackageGenerator:
    """Generate LaTeX package for Overleaf."""

    @staticmethod
    def generate_main_tex(
        parsed_paper: Dict,
        has_citations: bool = False,
        has_references: bool = False
    ) -> str:
        """Generate main.tex file."""
        logger.info("Generating main.tex")
        
        title = parsed_paper.get('title', 'TODO: Add Paper Title')
        abstract = parsed_paper.get('abstract', 'TODO: Add abstract here')
        extracted_text = parsed_paper.get('extracted_text', '')
        
        tex_content = r"""\documentclass{article}

\usepackage{neurips_2026}

% TODO: Verify this style file exists in your Overleaf project

\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{graphicx}
\usepackage{hyperref}

% Anonymous author block for NeurIPS
\author{Anonymous submission}

\title{""" + title + r"""}

\begin{document}

\maketitle

\begin{abstract}
""" + abstract + r"""
\end{abstract}

\section{Introduction}
% TODO: Add introduction text

\section{Related Work}
% TODO: Add related work

\section{Method}
% TODO: Add methodology

\section{Experiments}
% TODO: Add experimental setup and results

\section{Results}
% TODO: Add results and analysis

\section{Discussion}
% TODO: Add discussion

\section{Conclusion}
% TODO: Add conclusion

"""
        
        if has_references:
            tex_content += r"""\bibliographystyle{plainnat}
\bibliography{references}
"""
        
        if has_citations:
            tex_content += r"""\nocite{*}
"""
        else:
            tex_content += r"""% TODO: Add \cite{} commands for citations
"""
        
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

    @staticmethod
    def generate_readme() -> str:
        """Generate Overleaf instructions README."""
        logger.info("Generating README_OVERLEAF_INSTRUCTIONS.md")
        
        return """# Overleaf LaTeX Package Instructions

## Setup

1. **Create New Project**: 
   - Go to Overleaf.com
   - Create new project from uploaded ZIP

2. **Verify Template**:
   - Ensure `neurips_2026.sty` exists in project root
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
   - Verify all `\cite{}` commands have matching entries in `references.bib`
   - Check character encoding (UTF-8)

## Anonymity

- **For submission**: Keep `\\author{Anonymous submission}`
- **For preprint**: Replace with actual authors
- **For internal**: Use `\\usepackage[preprint]{neurips_2026}` if supported

## Compliance Checklist

Before submission, verify:

1. **Page Limit**: Confirm page count does not exceed conference limit
2. **References**: All citations have corresponding BibTeX entries
3. **Citations**: All \cite{} commands are present for referenced work
4. **Anonymity**: No author names, emails, or identifying information (unless preprint)
5. **Checklist**: Include required conference submission checklist if needed
6. **Template**: Using official neurips_2026 style

## TODO Tasks

Check main.tex for TODO comments:
- [ ] Add introduction
- [ ] Add related work
- [ ] Add method description
- [ ] Add experimental setup
- [ ] Add results
- [ ] Add discussion
- [ ] Add conclusion
- [ ] Verify all claims are supported by citations
- [ ] Fill in references.bib

## Support

For NeurIPS specific questions:
- Official Template: https://neurips.cc/
- Overleaf Help: https://www.overleaf.com/help

For compliance questions:
- Review compliance_report.json for detailed checklist
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

## Next Steps

1. Review issues in compliance_report.json
2. Address critical issues first
3. Fix warnings as possible
4. Verify all TODO items in main.tex
5. Test compilation in Overleaf
6. Download and submit

Note: This is an automated compliance check.
Manual review is still required before submission.
"""
