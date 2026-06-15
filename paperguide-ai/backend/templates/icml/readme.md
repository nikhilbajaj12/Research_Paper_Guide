# Overleaf LaTeX Package - ICML 2026

## Setup

1. **Create New Project**:
   - Go to Overleaf.com
   - Create new project from uploaded ZIP

2. **Verify Template**:
   - Ensure `icml_2026.sty` exists in project root
   - If missing, download from: https://icml.cc/Conferences/2026/StyleFiles

3. **Set Main File**:
   - In Overleaf menu, set `main.tex` as main file

4. **Add References**:
   - Edit `references.bib` with your BibTeX entries
   - Delete TODO examples
   - Do NOT leave empty `references.bib` if using citations

## Compilation

1. Recompile from scratch if references do not appear:
   - Delete auxiliary files: `.aux`, `.bbl`, `.log`
   - Recompile main.tex

2. If compilation fails:
   - Check `main.tex` for syntax errors
   - Verify all `\cite{}` commands have matching entries in `references.bib`
   - Check character encoding (UTF-8)

## Anonymity

- **For submission**: Keep `\author{Anonymous submission}`
- **For preprint**: Replace with actual authors

## Compliance Summary

- **Score**: {{compliance_score}}/100
- **Status**: {{compliance_status}}
- **Critical Issues**: {{critical_count}}
- **Warnings**: {{warnings_count}}

See `compliance_report.json` and `recommendations.md` for full details.

## Compliance Checklist

Before submission, verify:

1. **Page Limit**: Confirm page count does not exceed 8 pages (main content)
2. **References**: All citations have corresponding BibTeX entries
3. **Citations**: All `\cite{}` commands are present for referenced work
4. **Anonymity**: No author names, emails, or identifying information (unless preprint)
5. **Template**: Using official `icml_2026.sty`

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

- Official Template: https://icml.cc/Conferences/2026/StyleFiles
- Overleaf Help: https://www.overleaf.com/help

For compliance questions:
- Review `compliance_report.json` for detailed checklist
- Review `recommendations.md` for actionable fixes
