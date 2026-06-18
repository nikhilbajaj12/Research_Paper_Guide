"""AI Assistant service - provides intelligent guidance based on compliance results."""

from typing import Any, Dict, List, Optional

from ..core import get_logger
from ..utils.deduplication import deduplicate_recommendations
from .context_builder import ContextBuilder
from .prompt_builder import PromptBuilder

logger = get_logger(__name__)


class AssistantService:
    """AI Assistant service.

    Provides intelligent guidance to users about their compliance results.
    Does NOT modify files, re-run validators, or trigger package generation.
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
    ) -> Dict[str, str]:
        """Process a chat message and return AI-generated guidance.

        This method only reads compliance results. It never:
        - Triggers validators
        - Re-runs compliance analysis
        - Modifies uploaded papers
        - Triggers package generation
        """
        deduped_recommendations = deduplicate_recommendations(recommendations or [])

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

        return {"answer": answer}

    async def _generate_response(
        self, prompt: str, context: Dict[str, Any]
    ) -> str:
        """Generate a response using LLM or fallback logic.

        Currently uses a rule-based fallback. Replace with real LLM call
        when OPENAI_API_KEY is configured.
        """
        try:
            from ..utils.llm_utils import call_llm_api

            if _is_llm_configured():
                result = await call_llm_api(prompt)
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

        return "\n".join(lines)


def _is_llm_configured() -> bool:
    """Check if LLM API is configured."""
    try:
        from ..core.config import settings

        return bool(getattr(settings, "OPENAI_API_KEY", ""))
    except Exception:
        return False
