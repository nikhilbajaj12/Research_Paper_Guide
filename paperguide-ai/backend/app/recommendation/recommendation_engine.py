"""Recommendation engine — deterministic, rule-based fix suggestions."""

import re
from typing import Dict, List, Optional, Any
from ..schemas import ParsedDocument, ValidationResult, Recommendation
from ..core import get_logger

logger = get_logger(__name__)


class RecommendationEngine:
    """Generates specific, actionable recommendations from validation results.

    All logic is deterministic and rule-based. No LLM calls.
    """

    def generate(
        self,
        results: List[ValidationResult],
        parsed_doc: ParsedDocument,
        guidelines: Dict[str, Any],
    ) -> List[Recommendation]:
        """Generate recommendations from validation results.

        Only the first recommendation per category is kept to avoid
        duplicate / near-duplicate suggestions for the same issue class.
        """
        # Normalize: accept both ParsedDocument and plain dict
        if isinstance(parsed_doc, dict):
            valid_fields = ParsedDocument.__dataclass_fields__.keys()
            filtered = {k: v for k, v in parsed_doc.items() if k in valid_fields}
            filtered.setdefault("paper_id", "")
            filtered.setdefault("file_type", "")
            parsed_doc = ParsedDocument(**filtered)

        recommendations: List[Recommendation] = []
        seen_categories: set = set()

        category_handlers = {
            "anonymity": self._handle_anonymity,
            "page_limit": self._handle_page_limit,
            "missing_section": self._handle_missing_section,
            "template": self._handle_template,
            "margin": self._handle_margin,
            "references": self._handle_references,
            "citations": self._handle_citations,
            "claims_integrity": self._handle_claims,
        }

        for result in results:
            # Skip if we already have a recommendation for this category.
            if result.category in seen_categories:
                continue
            handler = category_handlers.get(result.category, self._handle_default)
            rec = handler(result, parsed_doc, guidelines)
            if rec is not None:
                seen_categories.add(result.category)
                recommendations.append(rec)

        return recommendations

    @staticmethod
    def _issue_id(result: ValidationResult) -> str:
        return f"rec_{result.category}_{hash(result.issue) & 0xFFFF}"

    # -------- Category handlers --------

    @staticmethod
    def _handle_anonymity(
        result: ValidationResult, doc: ParsedDocument, guidelines: Dict
    ) -> Optional[Recommendation]:
        issue = result.issue
        location = result.location

        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', issue + " " + location)
        if email_match:
            email = email_match.group()
            suggested = (
                f"Remove author email '{email}' from the author block. "
                f"Replace with 'Anonymous' or remove entirely for double-blind review."
            )
        elif "author" in issue.lower():
            suggested = (
                "Remove author names, affiliations, and acknowledgments from the title page. "
                "Use \\author{Anonymous} and \\institute{} with placeholder text."
            )
        else:
            marker_match = re.search(r"'(\w+)'", issue)
            marker = marker_match.group(1) if marker_match else "identifying information"
            suggested = (
                f"Review and remove '{marker}' references throughout the paper. "
                f"Self-citations should use 'Anonymous, et al.' or be omitted."
            )

        return Recommendation(
            issue_id=RecommendationEngine._issue_id(result),
            category="anonymity",
            can_auto_fix=False,
            suggested_action=suggested,
            issue=issue,
            location=location,
            severity=result.status,
            explanation=(
                f"Double-blind review requires removing all author-identifying information. "
                f"{issue}"
            ),
        )

    @staticmethod
    def _handle_page_limit(
        result: ValidationResult, doc: ParsedDocument, guidelines: Dict
    ) -> Optional[Recommendation]:
        issue = result.issue

        page_match = re.search(r'(\d+)\s*pages?\s*vs\s*(\d+)', issue)
        if page_match:
            page_count = int(page_match.group(1))
            max_pages = int(page_match.group(2))
            excess = page_count - max_pages

            main_tex = doc.main_tex_content or ""
            tex_section_count = len(re.findall(r'\\section\{', main_tex))
            common_cut = ["Appendix or supplementary material", "Related Work", "Experiments", "Introduction"]
            cut_targets = common_cut[:min(excess, len(common_cut))]

            suggested = (
                f"Current pages: {page_count}. Allowed pages: {max_pages}. "
                f"Reduce approximately {excess} page{'s' if excess > 1 else ''} from "
                f"{', '.join(cut_targets[:-1])} and {cut_targets[-1]}."
            )
        else:
            suggested = result.recommendation or "Reduce paper length to meet the page limit."

        return Recommendation(
            issue_id=RecommendationEngine._issue_id(result),
            category="page_limit",
            can_auto_fix=False,
            suggested_action=suggested,
            issue=result.issue,
            location=result.location,
            severity=result.status,
            explanation=f"Conference requires a maximum of {guidelines.get('max_pages', 'N/A')} pages.",
        )

    @staticmethod
    def _handle_missing_section(
        result: ValidationResult, doc: ParsedDocument, guidelines: Dict
    ) -> Optional[Recommendation]:
        issue = result.issue
        section_match = re.search(r"'([^']+)'", issue)
        section = section_match.group(1) if section_match else "the required section"

        existing = doc.sections or []
        insert_after = "Introduction"
        for candidate in ["Introduction", "Abstract", "Related Work"]:
            if candidate.lower() in [s.lower() for s in existing]:
                insert_after = candidate

        suggested = (
            f"Add a '{section}' section after {insert_after}. "
            f"Include subsections covering all required topics as specified in the conference guidelines."
        )

        return Recommendation(
            issue_id=RecommendationEngine._issue_id(result),
            category="missing_section",
            can_auto_fix=False,
            suggested_action=suggested,
            issue=result.issue,
            location=result.location,
            severity=result.status,
            explanation=f"The conference requires a '{section}' section.",
        )

    @staticmethod
    def _handle_template(
        result: ValidationResult, doc: ParsedDocument, guidelines: Dict
    ) -> Optional[Recommendation]:
        issue = result.issue

        docclass_match = re.search(r'\\documentclass\{(\w+)\}', doc.main_tex_content or "")
        used_class = docclass_match.group(1) if docclass_match else "unknown"

        suggested = (
            f"Use the official conference LaTeX template. "
            f"Replace \\documentclass{{{used_class}}} with the required document class. "
            f"Add \\usepackage{{...}} for conference-specific style files (e.g., \\usepackage{{neurips_2024}})."
        )

        return Recommendation(
            issue_id=RecommendationEngine._issue_id(result),
            category="template",
            can_auto_fix=False,
            suggested_action=suggested,
            issue=result.issue,
            location=result.location,
            severity=result.status,
            explanation=f"Template compliance issue: {issue}",
        )

    @staticmethod
    def _handle_margin(
        result: ValidationResult, doc: ParsedDocument, guidelines: Dict
    ) -> Optional[Recommendation]:
        top = guidelines.get("margin_top_cm", 2.54)
        bottom = guidelines.get("margin_bottom_cm", 2.54)
        left = guidelines.get("margin_left_cm", 2.54)
        right = guidelines.get("margin_right_cm", 2.54)

        suggested = (
            f"Add \\usepackage[top={top}cm, bottom={bottom}cm, left={left}cm, right={right}cm]{{geometry}} "
            f"to the LaTeX preamble to match conference margin requirements."
        )

        return Recommendation(
            issue_id=RecommendationEngine._issue_id(result),
            category="margin",
            can_auto_fix=True,
            suggested_action=suggested,
            issue=result.issue,
            location=result.location,
            severity=result.status,
            replacement_text=suggested,
            explanation=f"Required margins: top={top}cm, bottom={bottom}cm, left={left}cm, right={right}cm.",
        )

    @staticmethod
    def _handle_references(
        result: ValidationResult, doc: ParsedDocument, guidelines: Dict
    ) -> Optional[Recommendation]:
        if doc.bib_files:
            suggested = (
                f"Ensure the .bib file{'s' if len(doc.bib_files) > 1 else ''} "
                f"({', '.join(doc.bib_files[:3])}) is properly referenced with "
                f"\\bibliography{{{', '.join(f.replace('.bib', '') for f in doc.bib_files[:3])}}} in the main .tex file."
            )
        else:
            suggested = (
                "Add a References section with \\bibliography{references} and create a references.bib file "
                "containing all cited works in the required citation style."
            )

        return Recommendation(
            issue_id=RecommendationEngine._issue_id(result),
            category="references",
            can_auto_fix=False,
            suggested_action=suggested,
            issue=result.issue,
            location=result.location,
            severity=result.status,
            explanation="References section is required for academic submissions.",
        )

    @staticmethod
    def _handle_citations(
        result: ValidationResult, doc: ParsedDocument, guidelines: Dict
    ) -> Optional[Recommendation]:
        tex_content = doc.main_tex_content or ""
        tex_citation_count = len(re.findall(r'\\cite\{', tex_content))

        if tex_citation_count > 0:
            suggested = (
                f"{tex_citation_count} \\cite{{}} commands found in LaTeX source but citations were "
                f"not detected in the extracted text. Verify that citation keys resolve to entries "
                f"in the .bib file."
            )
        else:
            suggested = (
                "No citations detected. Add inline citations using \\cite{key} for each reference. "
                "Ensure each citation key exists in the .bib file."
            )

        return Recommendation(
            issue_id=RecommendationEngine._issue_id(result),
            category="citations",
            can_auto_fix=False,
            suggested_action=suggested,
            issue=result.issue,
            location=result.location,
            severity=result.status,
            explanation=result.issue,
        )

    @staticmethod
    def _handle_claims(
        result: ValidationResult, doc: ParsedDocument, guidelines: Dict
    ) -> Optional[Recommendation]:
        numeric_claims = doc.numeric_claims or []

        percentages = [c["value"] for c in numeric_claims if c.get("type") == "percentage"]
        metrics = [c["value"] for c in numeric_claims if c.get("type") == "metric"]
        speedups = [c["value"] for c in numeric_claims if c.get("type") == "speedup"]

        parts = []
        if percentages:
            examples = ", ".join(percentages[:5])
            parts.append(f"{len(percentages)} percentage{'s' if len(percentages) > 1 else ''} ({examples})")
        if metrics:
            examples = ", ".join(metrics[:5])
            parts.append(f"{len(metrics)} metric{'s' if len(metrics) > 1 else ''} ({examples})")
        if speedups:
            examples = ", ".join(speedups[:5])
            parts.append(f"{len(speedups)} speedup claim{'s' if len(speedups) > 1 else ''} ({examples})")

        if parts:
            claim_summary = "; ".join(parts)
            suggested = (
                f"Verify the following numeric claims against experiment logs or supplementary material: "
                f"{claim_summary}. "
                f"Remove or qualify any claims not directly supported by evidence."
            )
        else:
            suggested = (
                "Review all numeric claims for accuracy and ensure they are supported by "
                "experiment logs, tables, or citations. Add caveats for results that vary "
                "across runs."
            )

        return Recommendation(
            issue_id=RecommendationEngine._issue_id(result),
            category="claims_integrity",
            can_auto_fix=False,
            suggested_action=suggested,
            issue=result.issue,
            location=result.location,
            severity=result.status,
            explanation=f"Numeric claims should be verifiable: {result.issue}",
        )

    @staticmethod
    def _handle_default(
        result: ValidationResult, doc: ParsedDocument, guidelines: Dict
    ) -> Optional[Recommendation]:
        return Recommendation(
            issue_id=RecommendationEngine._issue_id(result),
            category=result.category,
            can_auto_fix=False,
            suggested_action=result.recommendation or "Review and address this issue.",
            issue=result.issue,
            location=result.location,
            severity=result.status,
            explanation=result.issue,
        )
