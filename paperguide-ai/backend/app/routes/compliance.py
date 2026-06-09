"""Compliance analysis routes."""

import os
import uuid
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from fastapi import Depends
from ..database import get_db
from ..schemas import ComplianceAnalyzeRequest, ComplianceReportResponse, FixSuggestion
from ..services.parser_service import ParserService
from ..checkers.anonymity_checker import AnonymityChecker
from ..checkers.page_limit_checker import PageLimitChecker
from ..checkers.reference_checker import ReferenceChecker
from ..checkers.citation_checker import CitationChecker
from ..checkers.claims_checker import ClaimsChecker
from ..core import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/compliance", tags=["compliance"])

PAPER_STORAGE = {}


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
        
        parser_service = ParserService()
        parsed_paper = parser_service.parse(storage_path, file_type)
        
        guidelines_dict = {
            "max_pages": 9,
            "requires_anonymity": True,
        }
        
        extracted_text = parsed_paper.get("extracted_text", "")
        issues = []
        passed_checks = []
        
        anonymity_checker = AnonymityChecker()
        anon_issues = anonymity_checker.check(extracted_text, parsed_paper)
        issues.extend(anon_issues)
        if not anon_issues:
            passed_checks.append("anonymity")
        
        page_checker = PageLimitChecker()
        page_issues = page_checker.check(parsed_paper, guidelines_dict)
        issues.extend(page_issues)
        if not page_issues:
            passed_checks.append("page_limit")
        
        ref_checker = ReferenceChecker()
        ref_issues = ref_checker.check(parsed_paper, guidelines_dict)
        issues.extend(ref_issues)
        if not ref_issues:
            passed_checks.append("references")
        
        citation_checker = CitationChecker()
        citation_issues = citation_checker.check(extracted_text, parsed_paper)
        issues.extend(citation_issues)
        if not citation_issues:
            passed_checks.append("citations")
        
        claims_checker = ClaimsChecker()
        claims_issues = claims_checker.check(extracted_text, parsed_paper)
        issues.extend(claims_issues)
        if not claims_issues:
            passed_checks.append("claims_integrity")
        
        critical_count = sum(1 for i in issues if i.get("severity") == "critical")
        warnings_count = sum(1 for i in issues if i.get("severity") == "warning")
        info_count = sum(1 for i in issues if i.get("severity") == "info")
        
        readiness_score = calculate_readiness_score(issues)
        overall_status = get_status_from_score(readiness_score, critical_count)
        
        fix_suggestions = generate_fix_suggestions(issues)
        
        return ComplianceReportResponse(
            project_id=request.paper_id,
            paper_id=paper_id,
            conference_id=request.conference_id,
            overall_status=overall_status,
            readiness_score=readiness_score,
            issues=[
                {
                    "issue_id": i.get("issue_id"),
                    "category": i.get("category"),
                    "severity": i.get("severity"),
                    "message": i.get("message"),
                    "location": i.get("location"),
                    "suggested_fix": i.get("suggested_fix"),
                    "needs_verification": i.get("needs_verification", False),
                }
                for i in issues
            ],
            passed_checks=passed_checks,
            warnings_count=warnings_count,
            critical_count=critical_count,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing compliance: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze compliance"
        )
