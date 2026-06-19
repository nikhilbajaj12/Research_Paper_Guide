"""Structure validator — combines PageLimit, Section, Template, Margin checks."""

import re
from typing import List, Optional
from ..schemas import ParsedDocument, ValidationResult
from ..checkers.page_limit_checker import PageLimitChecker
from ..core import get_logger
from .base_validator import BaseValidator 

logger = get_logger(__name__)


class StructureValidator(BaseValidator):
    """Validate paper structure: page limit, required sections, template, margins."""

    def __init__(self):
        super().__init__()
        self._page_checker = PageLimitChecker()

    async def validate(self, parsed_doc: ParsedDocument, guidelines: dict) -> List[ValidationResult]:
        logger.info("Validating paper structure (page limit, sections, template, margins)")
        results = []

        parsed_doc = self._to_parsed_document(parsed_doc)
        parsed_dict = parsed_doc.to_dict()

        # --- Page limit (delegate to legacy checker) ---
        page_issues = self._page_checker.check(parsed_dict, guidelines)
        for issue in page_issues:
            results.append(ValidationResult(
                status=issue.get("severity", "critical"),
                issue=issue.get("message", ""),
                location=issue.get("location", ""),
                recommendation=issue.get("suggested_fix", ""),
                category="page_limit",
                needs_verification=issue.get("needs_verification", False),
            ))

        # --- Required sections ---
        section_results = self._check_required_sections(parsed_doc, guidelines)
        results.extend(section_results)

        # --- Template compliance ---
        template_results = self._check_template(parsed_doc, guidelines)
        results.extend(template_results)

        # --- Margin compliance ---
        margin_results = self._check_margins(parsed_doc, guidelines)
        results.extend(margin_results)

        return results

    def _check_required_sections(self, parsed_doc: ParsedDocument, guidelines: dict) -> List[ValidationResult]:
        results = []
        required_sections = guidelines.get("required_sections", [])

        if not required_sections:
            return results

        found_sections = {s.strip().lower() for s in parsed_doc.sections if s}

        for section in required_sections:
            section_lower = section.strip().lower()
            if not any(section_lower in fs for fs in found_sections):
                results.append(ValidationResult(
                    status="warning",
                    issue=f"Required section '{section}' not found.",
                    location="Paper body",
                    recommendation=f"Add a '{section}' section to meet conference requirements.",
                    category="missing_section",
                    needs_verification=True,
                ))

        return results

    def _check_template(self, parsed_doc: ParsedDocument, guidelines: dict) -> List[ValidationResult]:
        results = []
        main_tex = parsed_doc.main_tex_content
        source_type = getattr(parsed_doc, "file_type", None) or getattr(parsed_doc, "source_type", None)

        if not main_tex:
            if source_type == "latex" or source_type == "zip":
                results.append(ValidationResult(
                    status="warning",
                    issue="No main .tex content found; cannot verify template compliance.",
                    location="LaTeX source",
                    recommendation="Ensure the main .tex file is included and contains a documentclass declaration.",
                    category="template",
                    needs_verification=True,
                ))
            return results

        docclass_match = re.search(r'\\documentclass\s*(\[.*?\])?\s*\{(.+?)\}', main_tex)
        used_class = docclass_match.group(2).strip() if docclass_match else None

        if not used_class:
            results.append(ValidationResult(
                status="warning",
                issue="No \\documentclass found in LaTeX source.",
                location="Main .tex file",
                recommendation="Add a \\documentclass declaration matching the conference template.",
                category="template",
                needs_verification=True,
            ))
        else:
            known_templates = ["article", "llncs", "neurips", "icml", "acl", "cvpr", "sigconf", "acmart"]
            if not any(t in used_class.lower() for t in known_templates):
                results.append(ValidationResult(
                    status="suggestion",
                    issue=f"Uncommon document class '{used_class}'. Verify it matches the conference template.",
                    location=f"\\documentclass{{{used_class}}}",
                    recommendation=f"Use the official conference template (e.g., \\documentclass{{neurips}}).",
                    category="template",
                    needs_verification=True,
                ))

        return results

    def _check_margins(self, parsed_doc: ParsedDocument, guidelines: dict) -> List[ValidationResult]:
        results = []
        margin_top = guidelines.get("margin_top_cm")
        margin_bottom = guidelines.get("margin_bottom_cm")

        if margin_top is None and margin_bottom is None:
            return results

        main_tex = parsed_doc.main_tex_content
        if not main_tex:
            results.append(ValidationResult(
                status="warning",
                issue="Cannot verify margin compliance — no LaTeX source available.",
                location="Page layout",
                recommendation="Use \\usepackage[margin=Xcm]{{geometry}} to set margins to the required values.",
                category="margin",
                needs_verification=True,
            ))
            return results

        has_geometry = bool(re.search(r'\\usepackage(\[.*?\])?\{(geometry)\}', main_tex))
        if not has_geometry:
            results.append(ValidationResult(
                status="suggestion",
                issue="No geometry package detected; margins may not match conference requirements.",
                location="Preamble",
                recommendation=f"Add \\usepackage[top={margin_top}cm, bottom={margin_bottom}cm, left=2.54cm, right=2.54cm]{{geometry}}.",
                category="margin",
                needs_verification=True,
            ))

        return results
