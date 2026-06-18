"""Compliance analysis routes."""

import asyncio
import os
import uuid
from typing import List
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from fastapi import Depends, status
from ..database import get_db
from ..schemas import ComplianceAnalyzeRequest, ComplianceReportResponse, FixSuggestion, ValidationResult, RecommendationDetail
from ..scoring import ScoringEngine
from ..recommendation import RecommendationEngine
from ..services.parser_service import ParserService
from ..cache.parsed_document_cache import ParsedDocumentCache
from ..conference import config_loader
from ..validators import BlindReviewValidator, StructureValidator, ResearchIntegrityValidator
from ..models import Paper as PaperModel
from ..core import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/compliance", tags=["compliance"])

PAPER_STORAGE = {}
COMPLIANCE_REPORT_STORAGE = {}


def resolve_conference_config(conference_id: str):
    """Resolve conference config with fallback for IDs like 'neurips-2025' -> 'neurips'."""
    config = config_loader.load(conference_id)
    resolved_id = conference_id

    if config is None and "-" in conference_id:
        base_id = conference_id.split("-", 1)[0]
        config = config_loader.load(base_id)
        if config is not None:
            resolved_id = base_id

    return config, resolved_id


def calculate_readiness_score(issues: list) -> int:
    """Calculate readiness score from issues."""
    score = 100
    for issue in issues:
        severity = issue.get('severity', 'info')
        if severity == 'critical':
            score -= 20
        elif severity == 'warning':
            score -= 8
        elif severity == 'info':
            score -= 2
    return max(0, min(100, score))


def get_status_from_score(score: int, critical_count: int) -> str:
    """Map score and critical count to status."""
    if score >= 90 and critical_count == 0:
        return "submission_ready"
    elif score >= 75 and critical_count == 0:
        return "needs_minor_fixes"
    elif score >= 50:
        return "needs_major_fixes"
    else:
        return "not_ready"


def generate_fix_suggestions(issues: list) -> list:
    """Generate fix suggestions for issues."""
    suggestions = []
    category_fixes = {
        'anonymity': (
            "Remove author names, affiliations, emails, acknowledgments, and self-identifying links for anonymous submission.",
            True
        ),
        'references': (
            "Add a References or Bibliography section and ensure citations resolve correctly.",
            False
        ),
        'citations': (
            "Add inline citations for all referenced work.",
            False
        ),
        'page_limit': (
            "Reduce main content or move non-essential material to appendix if allowed.",
            False
        ),
        'template': (
            "Use the official conference LaTeX template and required style file.",
            False
        ),
        'checklist': (
            "Add the required conference checklist before final submission.",
            False
        ),
        'claims_integrity': (
            "Verify numeric claims using experimental evidence or remove unsupported metrics.",
            False
        ),
    }
    
    seen_categories = set()
    for issue in issues:
        category = issue.get('category', 'unknown')
        if category not in seen_categories:
            seen_categories.add(category)
            fix_action, can_auto_fix = category_fixes.get(
                category,
                ("Review and address this issue.", False)
            )
            suggestions.append({
                "issue_id": f"fix_{category}",
                "can_auto_fix": can_auto_fix,
                "suggested_action": fix_action,
                "replacement_text": None,
                "explanation": f"This is a common {category} issue. {fix_action}",
            })
    
    return suggestions


def _rec_value(rec, key: str, default=None):
    """Read recommendation fields from either dataclass/object or dict."""
    if isinstance(rec, dict):
        return rec.get(key, default)
    return getattr(rec, key, default)


@router.post("/analyze", response_model=ComplianceReportResponse)
async def analyze_compliance(request: ComplianceAnalyzeRequest, db: Session = Depends(get_db)):
    """Analyze paper compliance with conference guidelines."""
    logger.info(f"Analyzing paper: {request.paper_id}, conference: {request.conference_id}")
    
    try:
        paper_id = request.paper_id
        storage_path = None
        file_type = None

        # Try in-memory first, fallback to DB
        if paper_id in PAPER_STORAGE:
            storage_path = PAPER_STORAGE[paper_id]["storage_path"]
            file_type = PAPER_STORAGE[paper_id]["file_type"]
        else:
            paper_db = db.query(PaperModel).filter(PaperModel.id == paper_id).first()
            if paper_db and paper_db.file_path:
                storage_path = paper_db.file_path
                file_type = os.path.splitext(storage_path)[1].lstrip('.')
            else:
                raise HTTPException(status_code=404, detail="Paper metadata not found in storage or database")
        
        if not os.path.exists(storage_path):
            logger.error(f"File missing at path: {storage_path}")
            raise HTTPException(
                status_code=404,
                detail="Paper file not found"
            )
        
        parsed_doc_cache = ParsedDocumentCache()
        parsed_paper = await parsed_doc_cache.get(paper_id, db)
        if parsed_paper is not None:
            logger.info(f"Cache HIT: paper={paper_id} (compliance analysis)")
        else:
            logger.info(f"Cache MISS: paper={paper_id} — parsing and repopulating (compliance analysis)")
            parser_service = ParserService()
            parsed_doc = parser_service.parse(storage_path, file_type, paper_id)
            await parsed_doc_cache.set(paper_id, parsed_doc, db)
            # Ensure we are working with a dictionary for engine compatibility
            parsed_paper = parsed_doc.model_dump() if hasattr(parsed_doc, "model_dump") else parsed_doc
            logger.info(f"Cache REFRESH: paper={paper_id} (compliance analysis)")

        config, resolved_conference_id = resolve_conference_config(request.conference_id)
        if config is None:
            raise HTTPException(
                status_code=404,
                detail=f"Conference config not found: {request.conference_id}"
            )
        guidelines_dict = config.to_guidelines_dict()

        # Run all validators in parallel
        blind_validator = BlindReviewValidator()
        structure_validator = StructureValidator()
        integrity_validator = ResearchIntegrityValidator()

        blind_result, structure_result, integrity_result = await asyncio.gather(
            blind_validator.validate(parsed_paper, guidelines_dict),
            structure_validator.validate(parsed_paper, guidelines_dict),
            integrity_validator.validate(parsed_paper, guidelines_dict),
        )

        all_results: List[ValidationResult] = []
        all_results.extend(blind_result)
        all_results.extend(structure_result)
        all_results.extend(integrity_result)

        # Convert ValidationResult to the dict format expected by the API
        issues = [r.to_issue_dict() for r in all_results]

        # Compute passed_checks: categories with zero issues
        category_counts: dict = {}
        for r in all_results:
            category_counts[r.category] = category_counts.get(r.category, 0) + 1

        passed_checks = []
        expected_categories = [
            "anonymity",
            "page_limit",
            "missing_section",
            "template",
            "margin",
            "references",
            "citations",
            "claims_integrity",
        ]
        if not guidelines_dict.get("requires_anonymity", False):
            passed_checks.append("anonymity")
        for cat in expected_categories:
            if cat == "anonymity" and not guidelines_dict.get("requires_anonymity", False):
                continue
            if cat not in category_counts:
                passed_checks.append(cat)

        # Score with ScoringEngine
        scoring_engine = ScoringEngine()
        score_result = scoring_engine.compute(all_results)

        # Generate recommendations
        rec_engine = RecommendationEngine()
        recommendations = rec_engine.generate(all_results, parsed_paper, guidelines_dict)

        readiness_score = score_result.score
        overall_status = score_result.status

        response = ComplianceReportResponse(
            project_id=request.paper_id,
            paper_id=paper_id,
            conference_id=resolved_conference_id,
            overall_status=overall_status,
            readiness_score=readiness_score,
            issues=issues,
            passed_checks=passed_checks,
            warnings_count=score_result.warnings_count,
            critical_count=score_result.critical_count,
            recommendations=[
                RecommendationDetail(
                    issue=_rec_value(rec, 'issue') or _rec_value(rec, 'suggested_action', 'Unknown Issue'),
                    location=_rec_value(rec, 'location') or _rec_value(rec, 'category', 'General'),
                    severity=_rec_value(rec, 'severity', 'warning'),
                    suggested_action=_rec_value(rec, 'suggested_action', ''),
                    explanation=_rec_value(rec, 'explanation', ''),
                    category=_rec_value(rec, 'category', 'general'),
                    can_auto_fix=_rec_value(rec, 'can_auto_fix', False),
                )
                for rec in recommendations
            ],
        )

        COMPLIANCE_REPORT_STORAGE[paper_id] = response.model_dump()
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing compliance: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze compliance"
        )
