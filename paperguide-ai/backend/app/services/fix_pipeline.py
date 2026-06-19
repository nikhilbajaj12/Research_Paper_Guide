"""Fix Pipeline orchestrator - coordinates the entire auto-fix workflow."""

import os
import uuid
from typing import Any, Dict, List, Optional

from ..core import get_logger, settings
from ..schemas.auto_fix_schemas import (
    AgentResult, BeforeAfterScore, ExecutionPlan,
    FixPipelineResult, FixStep,
)
from ..utils.deduplication import deduplicate_recommendations
from .audit_log import AuditLog
from .document_editor import DocumentEditor
from .mcp_service import MCPService
from ..agents.planner_agent import PlannerAgent
from ..agents.anonymity_fix_agent import AnonymityFixAgent
from ..agents.structure_fix_agent import StructureFixAgent
from ..agents.citation_fix_agent import CitationFixAgent
from ..agents.reference_fix_agent import ReferenceFixAgent
from ..agents.style_fix_agent import StyleFixAgent
from .llm_fixer import LLMFixer

logger = get_logger(__name__)

PIPELINE_STORAGE: Dict[str, Dict[str, Any]] = {}


class FixPipeline:
    """Orchestrates the end-to-end auto-fix pipeline.

    Flow:
    1. Planner creates execution plan
    2. Fix agents execute in priority order
    3. Document Editor applies changes
    4. Validation loop re-runs compliance
    5. Package generator creates submission package
    """

    AGENT_CLASSES = {
        "anonymity_fix": AnonymityFixAgent,
        "structure_fix": StructureFixAgent,
        "citation_fix": CitationFixAgent,
        "reference_fix": ReferenceFixAgent,
        "style_fix": StyleFixAgent,
    }

    def __init__(self):
        self.planner = PlannerAgent()
        self.document_editor = DocumentEditor()
        self.mcp = MCPService()
        self.audit_log = AuditLog()
        self.llm_fixer = LLMFixer()

    async def run(
        self,
        paper_id: str,
        conference_id: str,
        command: str,
        recommendations: List[Dict[str, Any]],
        parsed_paper: Dict[str, Any],
        guidelines: Dict[str, Any],
        storage_path: str,
        before_score: int,
        before_status: str,
        before_issues: List[Dict[str, Any]],
        before_passed_checks: List[str],
        compliance_runner: Any,
        optional_steps: Optional[List[str]] = None,
    ) -> FixPipelineResult:
        pipeline_id = f"fix_{uuid.uuid4().hex[:12]}"
        self.audit_log.start_pipeline(pipeline_id, command)

        deduped = deduplicate_recommendations(recommendations)
        plan = await self.planner.create_plan(deduped, command)

        if optional_steps:
            plan.steps = [s for s in plan.steps if s.agent in optional_steps or s.agent == "validation_loop"]

        agent_results: List[AgentResult] = []

        # Use LLM to fix issues first if they exist
        issues_to_fix = [r for r in recommendations if r.get("severity") in ("critical", "warning")]
        if issues_to_fix and settings.OPENAI_API_KEY:
            logger.info(f"Using LLM to fix {len(issues_to_fix)} critical/warning issues")
            self.audit_log.log_step("llm_fixer", "llm_fixer", "Apply LLM-based fixes", "running")
            try:
                fixed_paper = await self.llm_fixer.fix_document(
                    parsed_paper=parsed_paper,
                    issues=issues_to_fix,
                    guidelines=guidelines,
                    command=command,
                )
                parsed_paper = fixed_paper
                self.audit_log.log_step("llm_fixer", "llm_fixer", "Apply LLM-based fixes", "completed")
                agent_results.append(AgentResult(
                    agent="llm_fixer",
                    success=True,
                    changes_made=[f"Applied LLM fixes for {len(issues_to_fix)} issues"],
                ))
            except Exception as e:
                logger.error(f"LLM fixer failed: {e}")
                self.audit_log.log_error("llm_fixer", str(e))
                self.audit_log.log_step("llm_fixer", "llm_fixer", "Apply LLM-based fixes", "failed", str(e))

        for step in plan.steps:
            self.audit_log.log_step(step.step_id, step.agent, step.action, "running")
            step.status = "running"

            if step.agent == "validation_loop":
                step.status = "completed"
                continue

            agent_cls = self.AGENT_CLASSES.get(step.agent)
            if not agent_cls:
                self.audit_log.log_step(step.step_id, step.agent, step.action, "failed", "Unknown agent")
                step.status = "failed"
                continue

            try:
                agent = agent_cls()
                agent_relevant_recs = [r for r in deduped if agent.can_handle(r)]
                result = await agent.execute(
                    parsed_paper=parsed_paper,
                    recommendations=agent_relevant_recs or deduped,
                    guidelines=guidelines,
                    document_editor=self.document_editor,
                    audit_log=self.audit_log,
                )
                agent_results.append(result)
                step.status = "completed" if result.success else "failed"
                self.audit_log.log_step(step.step_id, step.agent, step.action, step.status)
            except Exception as e:
                logger.error(f"Agent {step.agent} failed: {e}")
                self.audit_log.log_error(step.agent, str(e))
                agent_results.append(AgentResult(agent=step.agent, success=False, changes_made=[], error=str(e)))
                step.status = "failed"

        score_comparison = await self._run_validation_loop(
            paper_id=paper_id,
            conference_id=conference_id,
            parsed_paper=parsed_paper,
            before_score=before_score,
            before_status=before_status,
            compliance_runner=compliance_runner,
            audit_log=self.audit_log,
        )

        package_path = await self._generate_package(
            paper_id=paper_id,
            conference_id=conference_id,
            parsed_paper=parsed_paper,
            storage_path=storage_path,
        )

        self.audit_log.complete_pipeline(score_comparison is not None)

        result = FixPipelineResult(
            plan=plan,
            agent_results=agent_results,
            score_comparison=score_comparison,
            package_path=package_path,
            package_download_url=f"/api/v1/auto-fix/{pipeline_id}/download" if package_path else None,
            audit_log=self.audit_log.get_entries(),
            success=score_comparison is not None,
        )

        PIPELINE_STORAGE[pipeline_id] = {
            "status": "completed",
            "result": result.model_dump(),
            "package_path": package_path,
            "parsed_paper": parsed_paper,
        }

        return result

    async def _run_validation_loop(
        self,
        paper_id: str,
        conference_id: str,
        parsed_paper: Dict[str, Any],
        before_score: int,
        before_status: str,
        compliance_runner: Any,
        audit_log: AuditLog,
    ) -> Optional[BeforeAfterScore]:
        """Re-run compliance analysis and compare scores."""
        try:
            from ..cache.parsed_document_cache import ParsedDocumentCache
            cache = ParsedDocumentCache()

            from ..schemas import ParsedDocument
            doc = ParsedDocument.from_dict(parsed_paper) if isinstance(parsed_paper, dict) and not hasattr(parsed_paper, 'paper_id') else parsed_paper
            if hasattr(doc, 'paper_id'):
                pass
            elif isinstance(parsed_paper, dict) and 'paper_id' in parsed_paper:
                from ..schemas import ParsedDocument as PD
                doc = PD.from_dict(parsed_paper)

            if hasattr(doc, 'paper_id') and hasattr(doc, 'to_dict'):
                from ..database import SessionLocal
                db = SessionLocal()
                try:
                    await cache.set(paper_id, doc, db)
                finally:
                    db.close()

            after_response = await compliance_runner(
                paper_id=paper_id,
                conference_id=conference_id,
                parsed_override=parsed_paper,
            )

            after_score = getattr(after_response, 'readiness_score', 0) if hasattr(after_response, 'readiness_score') else after_response.get('readiness_score', 0)
            after_status = getattr(after_response, 'overall_status', 'unknown') if hasattr(after_response, 'overall_status') else after_response.get('overall_status', 'unknown')

            comparison = BeforeAfterScore(
                before_score=before_score,
                after_score=after_score,
                improvement=after_score - before_score,
                before_status=before_status,
                after_status=after_status,
            )
            audit_log.log_score_comparison(before_score, after_score)
            return comparison
        except Exception as e:
            logger.error(f"Validation loop error: {e}")
            audit_log.log_error("validation_loop", str(e))
            return None

    async def _generate_package(
        self,
        paper_id: str,
        conference_id: str,
        parsed_paper: Dict[str, Any],
        storage_path: str,
    ) -> Optional[str]:
        """Generate a submission package from the fixed document."""
        try:
            from ..services.package_service import PackageService
            from ..routes.compliance import COMPLIANCE_REPORT_STORAGE

            report = COMPLIANCE_REPORT_STORAGE.get(paper_id, {})
            ps = PackageService()
            pkg_id, metadata = ps.generate_package(
                paper_id=paper_id,
                conference_id=conference_id,
                parsed_paper=parsed_paper,
                compliance_report=report,
            )
            zip_path = metadata.get("zip_file_path", "")
            logger.info(f"Package generated: {zip_path}")
            return zip_path
        except Exception as e:
            logger.error(f"Package generation error: {e}")
            return None


async def run_compliance_for_validation(
    paper_id: str,
    conference_id: str,
    parsed_override: Optional[Dict[str, Any]] = None,
) -> Any:
    """Run compliance analysis for validation loop purposes."""
    from ..routes.compliance import (
        analyze_compliance,
        ComplianceAnalyzeRequest,
        PAPER_STORAGE,
    )
    from ..database import SessionLocal

    if parsed_override:
        from ..models.paper_analysis import PaperAnalysis
        from ..cache.parsed_document_cache import ParsedDocumentCache
        import json
        from ..schemas import ParsedDocument

        doc = ParsedDocument.from_dict(parsed_override)
        cache = ParsedDocumentCache()
        db = SessionLocal()
        try:
            await cache.set(paper_id, doc, db)
        finally:
            db.close()

    from ..schemas import ComplianceAnalyzeRequest
    req = ComplianceAnalyzeRequest(paper_id=paper_id, conference_id=conference_id)
    db = SessionLocal()
    try:
        result = await analyze_compliance(req, db=db)
        return result
    finally:
        db.close()
