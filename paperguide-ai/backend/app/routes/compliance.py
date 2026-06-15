"""Compliance analysis routes."""

import asyncio
import os
import uuid
from typing import List
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from fastapi import Depends
from ..database import get_db
from ..schemas import ComplianceAnalyzeRequest, ComplianceReportResponse, FixSuggestion, ValidationResult, RecommendationDetail
from ..scoring import ScoringEngine
from ..recommendation import RecommendationEngine
from ..services.parser_service import ParserService
from ..cache.parsed_document_cache import ParsedDocumentCache
from ..conference import config_loader
from ..validators import BlindReviewValidator, StructureValidator, ResearchIntegrityValidator
from ..core import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/compliance", tags=["compliance"])

PAPER_STORAGE = {}
COMPLIANCE_REPORT_STORAGE = {}


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


@router.post("/analyze", response_model=ComplianceReportResponse)
async def analyze_compliance(request: ComplianceAnalyzeRequest, db: Session = Depends(get_db)):
    """Analyze paper compliance with conference guidelines."""
    logger.info(f"Analyzing paper: {request.paper_id}, conference: {request.conference_id}")
    
    try:
        paper_id = request.paper_id
        if paper_id not in PAPER_STORAGE:
            raise HTTPException(
                status_code=404,
                detail=f"Paper not found: {paper_id}"
            )
        
        paper_info = PAPER_STORAGE[paper_id]
        storage_path = paper_info["storage_path"]
        file_type = paper_info["file_type"]
        
        if not os.path.exists(storage_path):
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
            parsed_paper = parser_service.parse(storage_path, file_type, paper_id)
            await parsed_doc_cache.set(paper_id, parsed_paper, db)
            logger.info(f"Cache REFRESH: paper={paper_id} (compliance analysis)")

        config = config_loader.load(request.conference_id)
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
            conference_id=request.conference_id,
            overall_status=overall_status,
            readiness_score=readiness_score,
            issues=issues,
            passed_checks=passed_checks,
            warnings_count=score_result.warnings_count,
            critical_count=score_result.critical_count,
            recommendations=[
                RecommendationDetail(
                    issue=rec.issue or rec.suggested_action,
                    location=rec.location or rec.category,
                    severity=rec.severity or "warning",
                    suggested_action=rec.suggested_action,
                    explanation=rec.explanation,
                    category=rec.category,
                    can_auto_fix=rec.can_auto_fix,
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
