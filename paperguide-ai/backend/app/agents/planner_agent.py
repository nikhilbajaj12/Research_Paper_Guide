"""Planner Agent - creates execution plans from recommendations."""

import uuid
from typing import Any, Dict, List, Optional

from ..schemas.auto_fix_schemas import ExecutionPlan, FixStep
from ..core import get_logger

logger = get_logger(__name__)

AGENT_MAP = {
    "anonymity": "anonymity_fix",
    "missing_section": "structure_fix",
    "citations": "citation_fix",
    "references": "reference_fix",
    "style": "style_fix",
}

CATEGORY_PRIORITY = [
    "anonymity",
    "missing_section",
    "template",
    "margin",
    "references",
    "citations",
    "page_limit",
    "claims_integrity",
]


class PlannerAgent:
    """Creates prioritized execution plans from compliance recommendations."""

    async def create_plan(
        self,
        recommendations: List[Dict[str, Any]],
        user_command: str = "Fix all issues",
    ) -> ExecutionPlan:
        """Analyze recommendations and produce a sorted execution plan."""
        plan_id = f"plan_{uuid.uuid4().hex[:8]}"
        steps: List[FixStep] = []
        step_num = 0
        seen_categories = set()

        categorized = self._categorize_recommendations(recommendations)
        for cat in CATEGORY_PRIORITY:
            if cat not in categorized:
                continue
            if cat in seen_categories:
                continue
            seen_categories.add(cat)

            agent = AGENT_MAP.get(cat)
            if not agent:
                continue

            recs = categorized[cat]
            issue_msgs = [r.get("issue", r.get("message", "")) for r in recs[:3]]
            step_num += 1
            steps.append(FixStep(
                step_id=f"step_{step_num:02d}",
                agent=agent,
                action=f"Fix {cat.replace('_', ' ')} issues",
                target=cat,
                details="; ".join(issue_msgs) if issue_msgs else f"Resolve {cat} compliance issues",
                status="pending",
            ))

        if not steps:
            steps.append(FixStep(
                step_id="step_01",
                agent="style_fix",
                action="Apply general style improvements",
                target="style",
                details="Improve grammar, readability, and consistency",
                status="pending",
            ))

        step_num += 1
        steps.append(FixStep(
            step_id=f"step_{step_num:02d}",
            agent="validation_loop",
            action="Re-run compliance validation",
            target="validation",
            details="Validate fixes by re-running compliance analysis",
            status="pending",
        ))

        summary = self._generate_summary(steps, user_command)
        return ExecutionPlan(plan_id=plan_id, steps=steps, summary=summary)

    def _categorize_recommendations(
        self, recommendations: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        result: Dict[str, List[Dict[str, Any]]] = {}
        for rec in recommendations:
            cat = rec.get("category", "unknown")
            if cat not in result:
                result[cat] = []
            result[cat].append(rec)
        return result

    def _generate_summary(self, steps: List[FixStep], command: str) -> str:
        total = len([s for s in steps if s.agent != "validation_loop"])
        return (
            f"Plan created for command: '{command}'. "
            f"Will execute {total} fix step(s) followed by validation. "
            f"Agents: {', '.join(s.agent for s in steps if s.agent != 'validation_loop')}."
        )
