"""AI Assistant service - provides intelligent guidance and can auto-fix papers."""

import re
from typing import Any, Dict, List, Optional

from ..core import get_logger
from ..utils.deduplication import deduplicate_recommendations
from .context_builder import ContextBuilder
from .prompt_builder import PromptBuilder

logger = get_logger(__name__)

FIX_INTENT_PATTERNS = [
    re.compile(r"\bfix\b.*\b(?:paper|document|all|issues?|problems?)\b", re.IGNORECASE),
    re.compile(r"\b(?:correct|repair|resolve|rectify)\b.*\b(?:paper|document|all|issues?)\b", re.IGNORECASE),
    re.compile(r"\b(?:make|get)\b.*\b(?:ready|submittable|compliant|acceptable)\b", re.IGNORECASE),
    re.compile(r"\b(?:improve|update|enhance|polish)\b.*\b(?:paper|document|score)\b", re.IGNORECASE),
    re.compile(r"\brun\b.*\b(?:auto.fix|pipeline|fix)\b", re.IGNORECASE),
    re.compile(r"\bauto.?fix\b", re.IGNORECASE),
    re.compile(r"\bapply\b.*\b(?:all|fixes?|changes?|corrections?)\b", re.IGNORECASE),
]


def _is_fix_intent(user_message: str) -> bool:
    """Detect whether the user is asking to automatically fix the paper."""
    return any(p.search(user_message) for p in FIX_INTENT_PATTERNS)


class AssistantService:
    """AI Assistant service.

    Provides intelligent guidance to users about their compliance results.
    When the user asks to fix the paper, it triggers the auto-fix pipeline.
    """

    def __init__(self):
        self.context_builder = ContextBuilder()
        self.prompt_builder = PromptBuilder()

    async def chat(
        self,
        conference: Optional[Dict[str, Any]] = None,
        compliance_score: int = 0,
        critical_issues: Optional[List[Dict[str, Any]]] = None,
        warnings: Optional[List[Dict[str, Any]]] = None,
        passed_checks: Optional[List[str]] = None,
        recommendations: Optional[List[Dict[str, Any]]] = None,
        user_message: str = "",
        paper_id: Optional[str] = None,
        conference_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Process a chat message and return AI-generated guidance.

        If the user asks to fix the paper AND paper_id is provided,
        triggers the auto-fix pipeline and returns the fix result.
        """
        deduped_recommendations = deduplicate_recommendations(recommendations or [])

        if _is_fix_intent(user_message) and paper_id and conference_id:
            return await self._run_fix_pipeline(
                paper_id=paper_id,
                conference_id=conference_id,
                recommendations=deduped_recommendations,
                user_message=user_message,
            )

        context = self.context_builder.build(
            conference=conference,
            compliance_score=compliance_score,
            critical_issues=critical_issues,
            warnings=warnings,
            passed_checks=passed_checks,
            recommendations=deduped_recommendations,
        )

        system_prompt = self.prompt_builder.build_system_prompt(
            conference=conference,
            compliance_score=compliance_score,
            critical_issues=critical_issues,
            warnings=warnings,
            passed_checks=passed_checks,
            recommendations=deduped_recommendations,
            user_message=user_message,
        )

        answer = await self._generate_response(system_prompt, context)

        return {"answer": answer, "fix_run": False}

    async def _run_fix_pipeline(
        self,
        paper_id: str,
        conference_id: str,
        recommendations: List[Dict[str, Any]],
        user_message: str,
    ) -> Dict[str, Any]:
        """Run the auto-fix pipeline and return results."""
        from .fix_pipeline import FixPipeline
        from ..routes.compliance import PAPER_STORAGE, COMPLIANCE_REPORT_STORAGE

        logger.info(f"Assistant triggering fix pipeline for paper={paper_id}")

        report = COMPLIANCE_REPORT_STORAGE.get(paper_id)
        paper_info = PAPER_STORAGE.get(paper_id)
        if not report or not paper_info:
            return {
                "answer": "I couldn't find a compliance report or paper. Please upload and analyze your paper first.",
                "fix_run": False,
            }

        from ..conference import config_loader
        config = config_loader.load(conference_id)
        if config is None and "-" in conference_id:
            config = config_loader.load(conference_id.split("-", 1)[0])
        guidelines_dict = config.to_guidelines_dict() if config else {}

        from ..cache.parsed_document_cache import ParsedDocumentCache
        from ..database import SessionLocal
        from ..services.document_editor import DocumentEditor

        cache = ParsedDocumentCache()
        db = SessionLocal()
        try:
            parsed_paper = await cache.get(paper_id, db)
        finally:
            db.close()

        if parsed_paper is None:
            return {
                "answer": "I couldn't find a parsed version of your paper. Please re-upload and analyze it.",
                "fix_run": False,
            }

        parsed_dict = parsed_paper.to_dict()
        before_score = report.get("readiness_score", 0)
        before_status = report.get("overall_status", "unknown")
        before_issues = report.get("issues", [])
        before_passed = report.get("passed_checks", [])

        pipeline = FixPipeline()
        try:
            result = await pipeline.run(
                paper_id=paper_id,
                conference_id=conference_id,
                command=user_message,
                recommendations=recommendations,
                parsed_paper=parsed_dict,
                guidelines=guidelines_dict,
                storage_path=paper_info["storage_path"],
                before_score=before_score,
                before_status=before_status,
                before_issues=before_issues,
                before_passed_checks=before_passed,
                compliance_runner=self._run_compliance_check,
            )
        except Exception as e:
            logger.error(f"Fix pipeline failed: {e}")
            return {
                "answer": f"I tried to fix your paper but encountered an error: {str(e)}",
                "fix_run": False,
            }

        answer_lines = ["## Auto-Fix Complete\n"]
        if result.success:
            changes = []
            for ar in result.agent_results:
                for c in ar.changes_made:
                    changes.append(f"  - **{ar.agent}**: {c}")

            if changes:
                answer_lines.append("I applied the following changes:\n")
                answer_lines.extend(changes)
                answer_lines.append("")

            if result.score_comparison:
                sc = result.score_comparison
                answer_lines.append(
                    f"**Score improvement**: {sc.before_score} → {sc.after_score} "
                    f"({'+' if sc.improvement >= 0 else ''}{sc.improvement} points)"
                )
                answer_lines.append("")

            if result.package_download_url:
                answer_lines.append(
                    "A **fixed package** is ready for download. "
                    "You can also generate an Overleaf package below."
                )
            else:
                answer_lines.append(
                    "You can now generate an Overleaf package from the fixed version "
                    "using the button below."
                )
        else:
            answer_lines.append(f"The fix pipeline encountered an issue: {result.error or 'Unknown error'}")

        answer = "\n".join(answer_lines)

        return {
            "answer": answer,
            "fix_run": True,
            "pipeline_id": result.plan.plan_id.replace("plan_", "fix_") if result.plan else None,
            "download_url": result.package_download_url,
            "fix_summary": f"Score: {result.score_comparison.before_score} → {result.score_comparison.after_score}" if result.score_comparison else None,
        }

    async def _run_compliance_check(self, paper_id: str, conference_id: str, parsed_override=None):
        """Run compliance check for the validation loop."""
        from ..routes.compliance import analyze_compliance, ComplianceAnalyzeRequest
        from ..database import SessionLocal
        from ..cache.parsed_document_cache import ParsedDocumentCache

        if parsed_override:
            from ..schemas import ParsedDocument
            doc = ParsedDocument.from_dict(parsed_override)
            cache = ParsedDocumentCache()
            db = SessionLocal()
            try:
                await cache.set(paper_id, doc, db)
            finally:
                db.close()

        db = SessionLocal()
        try:
            result = await analyze_compliance(
                ComplianceAnalyzeRequest(paper_id=paper_id, conference_id=conference_id),
                db=db,
            )
            return result
        finally:
            db.close()

    async def _generate_response(
        self, prompt: str, context: Dict[str, Any]
    ) -> str:
        """Generate a response using LLM or fallback logic."""
        try:
            from ..utils.llm_utils import call_llm_api

            if _is_llm_configured():
                system_prompt = (
                    "You are PaperGuide AI, an expert academic-paper compliance assistant. "
                    "You help researchers prepare their papers for conference submission. "
                    "Be concise, actionable, and specific. When suggesting fixes, reference "
                    "exact LaTeX commands or document sections. Always end by offering to "
                    "auto-fix the paper if the user says 'fix my paper'."
                )
                result = await call_llm_api(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=0.4,
                    max_tokens=1024,
                )
                if result:
                    return result
        except Exception as e:
            logger.warning(f"LLM call failed, using fallback: {e}")

        return self._fallback_response(context)

    def _fallback_response(self, context: Dict[str, Any]) -> str:
        """Generate a deterministic fallback response based on context."""
        score = context.get("compliance_score", 0)
        critical = context.get("critical_issues", [])
        warnings_list = context.get("warnings", [])
        passed = context.get("passed_checks", [])
        recommendations = context.get("recommendations", [])

        lines = []

        if score < 50:
            lines.append("Your paper needs significant improvements before submission.")
        elif score < 75:
            lines.append("Your paper has some issues that need attention.")
        elif score < 90:
            lines.append("Your paper is mostly ready with minor issues to address.")
        else:
            lines.append("Your paper is in good shape for submission.")

        if critical:
            lines.append("")
            lines.append(f"**Critical Issues ({len(critical)}):**")
            for issue in critical:
                msg = issue.get("message", issue.get("issue", "Unknown issue"))
                lines.append(f"- {msg}")

        if warnings_list:
            lines.append("")
            lines.append(f"**Warnings ({len(warnings_list)}):**")
            for warn in warnings_list:
                msg = warn.get("message", warn.get("issue", "Unknown warning"))
                lines.append(f"- {msg}")

        if passed:
            lines.append("")
            lines.append(f"**Passed Checks ({len(passed)}):**")
            lines.append(", ".join(p.replace("_", " ") for p in passed))

        if recommendations:
            lines.append("")
            lines.append("**Recommended Actions:**")
            for rec in recommendations:
                action = rec.get("suggested_action", rec.get("issue", "Review issue"))
                lines.append(f"- {action}")

        if not lines:
            lines.append(
                "I don't have enough information to provide guidance. "
                "Please run a compliance analysis first."
            )

        lines.append("")
        lines.append("---")
        lines.append("Would you like me to automatically fix these issues? Just say **fix my paper**!")

        return "\n".join(lines)


def _is_llm_configured() -> bool:
    """Check if LLM API is configured."""
    try:
        from ..core.config import settings

        return bool(getattr(settings, "OPENAI_API_KEY", ""))
    except Exception:
        return False
