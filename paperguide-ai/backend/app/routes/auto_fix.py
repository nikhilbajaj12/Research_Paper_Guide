"""Auto-fix pipeline routes - AI-powered document fixing."""

import os
import json
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.auto_fix_schemas import (
    AutoFixRequest,
    AutoFixStatusResponse,
    FixPipelineResult,
)
from ..services.fix_pipeline import FixPipeline, PIPELINE_STORAGE, run_compliance_for_validation
from ..services.parser_service import ParserService
from ..cache.parsed_document_cache import ParsedDocumentCache
from ..conference import config_loader
from .compliance import PAPER_STORAGE as COMPLIANCE_PAPER_STORAGE
from .compliance import COMPLIANCE_REPORT_STORAGE
from ..core import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/auto-fix", tags=["auto-fix"])


def resolve_conference_config(conference_id: str):
    config = config_loader.load(conference_id)
    resolved_id = conference_id
    if config is None and "-" in conference_id:
        base_id = conference_id.split("-", 1)[0]
        config = config_loader.load(base_id)
        if config is not None:
            resolved_id = base_id
    return config, resolved_id


@router.post("/run", response_model=AutoFixStatusResponse)
async def run_auto_fix(request: AutoFixRequest, db: Session = Depends(get_db)):
    """Run the full auto-fix pipeline on a paper."""
    logger.info(f"Auto-fix requested: paper={request.paper_id}, command={request.command}")

    try:
        paper_id = request.paper_id
        if paper_id not in COMPLIANCE_PAPER_STORAGE:
            raise HTTPException(status_code=404, detail="Paper not found. Upload first.")

        paper_info = COMPLIANCE_PAPER_STORAGE[paper_id]
        storage_path = paper_info["storage_path"]
        file_type = paper_info["file_type"]

        if not os.path.exists(storage_path):
            raise HTTPException(status_code=404, detail="Paper file not found")

        config, resolved_conference_id = resolve_conference_config(request.conference_id)
        if config is None:
            raise HTTPException(status_code=404, detail="Conference config not found")
        guidelines_dict = config.to_guidelines_dict()

        parsed_doc_cache = ParsedDocumentCache()
        parsed_paper = await parsed_doc_cache.get(paper_id, db)
        if parsed_paper is not None:
            parsed_dict = parsed_paper.to_dict()
        else:
            parser_service = ParserService()
            parsed_doc = parser_service.parse(storage_path, file_type, paper_id)
            await parsed_doc_cache.set(paper_id, parsed_doc, db)
            parsed_dict = parsed_doc.to_dict()

        report = COMPLIANCE_REPORT_STORAGE.get(paper_id)
        if not report:
            raise HTTPException(status_code=409, detail="Run compliance analysis first")

        recommendations = report.get("recommendations", [])
        before_score = report.get("readiness_score", 0)
        before_status = report.get("overall_status", "unknown")
        before_issues = report.get("issues", [])
        before_passed = report.get("passed_checks", [])

        pipeline = FixPipeline()

        result = await pipeline.run(
            paper_id=paper_id,
            conference_id=resolved_conference_id,
            command=request.command,
            recommendations=recommendations,
            parsed_paper=parsed_dict,
            guidelines=guidelines_dict,
            storage_path=storage_path,
            before_score=before_score,
            before_status=before_status,
            before_issues=before_issues,
            before_passed_checks=before_passed,
            compliance_runner=_run_compliance_check,
            optional_steps=request.steps,
        )

        pipeline_id = result.plan.plan_id.replace("plan_", "fix_")

        return AutoFixStatusResponse(
            pipeline_id=pipeline_id,
            status="completed" if result.success else "failed",
            progress=100 if result.success else 50,
            result=result,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Auto-fix error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Auto-fix failed: {str(e)}")


@router.get("/{pipeline_id}/status", response_model=AutoFixStatusResponse)
async def get_pipeline_status(pipeline_id: str):
    """Get the status of a running/completed fix pipeline."""
    entry = PIPELINE_STORAGE.get(pipeline_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return AutoFixStatusResponse(
        pipeline_id=pipeline_id,
        status=entry["status"],
        progress=100 if entry["status"] == "completed" else 0,
        result=entry.get("result"),
    )


@router.get("/{pipeline_id}/download")
async def download_fixed_package(pipeline_id: str):
    """Download the fixed package ZIP."""
    entry = PIPELINE_STORAGE.get(pipeline_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    pkg_path = entry.get("package_path")
    if not pkg_path or not os.path.exists(pkg_path):
        raise HTTPException(status_code=404, detail="Package file not found")
    return FileResponse(
        path=pkg_path,
        filename=os.path.basename(pkg_path),
        media_type="application/zip",
    )


async def _run_compliance_check(paper_id: str, conference_id: str, parsed_override=None):
    """Helper to run compliance analysis for the validation loop."""
    from ..routes.compliance import analyze_compliance, ComplianceAnalyzeRequest
    from ..database import SessionLocal

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
