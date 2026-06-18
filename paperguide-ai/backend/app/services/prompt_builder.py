"""AI Assistant prompt builder."""

from typing import Any, Dict, List, Optional


SYSTEM_PROMPT_TEMPLATE = """You are an expert Conference Submission Assistant.
You help researchers prepare papers for conference submission.

Conference Information:
{conference}

Compliance Score:
{score}

Critical Issues:
{critical_issues}

Warnings:
{warnings}

Passed Checks:
{passed_checks}

Recommendations:
{recommendations}

Instructions:
1. Explain recommendations clearly.
2. Group related issues.
3. Prioritize critical issues first.
4. Suggest practical fixes.
5. Be concise but actionable.
6. Never invent conference rules.
7. Never claim that files were modified.
8. Never claim package generation occurred.
9. Only provide guidance and recommendations.
10. If user asks to fix the document automatically,
   explain that automatic fixing will be available
   in a future version.

User Question:
{user_message}"""


class PromptBuilder:
    """Build prompts for the AI assistant."""

    def build_context(
        self,
        conference: Optional[Dict[str, Any]] = None,
        compliance_score: int = 0,
        critical_issues: Optional[List[Dict[str, Any]]] = None,
        warnings: Optional[List[Dict[str, Any]]] = None,
        passed_checks: Optional[List[str]] = None,
        recommendations: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """Build structured context string."""
        parts = []

        conf_str = self._format_conference(conference)
        parts.append(f"Conference Information:\n{conf_str}")
        parts.append(f"Compliance Score:\n{compliance_score}")
        parts.append(f"Critical Issues:\n{self._format_list(critical_issues)}")
        parts.append(f"Warnings:\n{self._format_list(warnings)}")
        parts.append(f"Passed Checks:\n{self._format_list(passed_checks)}")
        parts.append(f"Recommendations:\n{self._format_recommendations(recommendations)}")

        return "\n\n".join(parts)

    def build_system_prompt(
        self,
        conference: Optional[Dict[str, Any]] = None,
        compliance_score: int = 0,
        critical_issues: Optional[List[Dict[str, Any]]] = None,
        warnings: Optional[List[Dict[str, Any]]] = None,
        passed_checks: Optional[List[str]] = None,
        recommendations: Optional[List[Dict[str, Any]]] = None,
        user_message: str = "",
    ) -> str:
        """Build the full system prompt with context and user message."""
        context = self.build_context(
            conference=conference,
            compliance_score=compliance_score,
            critical_issues=critical_issues,
            warnings=warnings,
            passed_checks=passed_checks,
            recommendations=recommendations,
        )

        return SYSTEM_PROMPT_TEMPLATE.format(
            conference=conference or {},
            score=compliance_score,
            critical_issues=self._format_list(critical_issues),
            warnings=self._format_list(warnings),
            passed_checks=self._format_list(passed_checks),
            recommendations=self._format_recommendations(recommendations),
            user_message=user_message,
        )

    def _format_conference(self, conference: Optional[Dict[str, Any]]) -> str:
        if not conference:
            return "No conference selected."
        lines = []
        for key, value in conference.items():
            lines.append(f"  - {key}: {value}")
        return "\n".join(lines)

    def _format_list(self, items: Optional[List]) -> str:
        if not items:
            return "  None"
        lines = []
        for item in items:
            if isinstance(item, dict):
                lines.append(f"  - {item.get('message', item.get('issue', str(item)))}")
            else:
                lines.append(f"  - {item}")
        return "\n".join(lines)

    def _format_recommendations(self, recommendations: Optional[List[Dict[str, Any]]]) -> str:
        if not recommendations:
            return "  None"
        lines = []
        for rec in recommendations:
            issue = rec.get("issue", rec.get("suggested_action", "Unknown"))
            category = rec.get("category", "general")
            severity = rec.get("severity", "info")
            lines.append(f"  - [{severity}] ({category}) {issue}")
        return "\n".join(lines)
