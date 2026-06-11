"""Pydantic schemas for the API."""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import date, datetime
from enum import Enum


# ============ Common Schemas ============

class ErrorResponse(BaseModel):
    """Standard error response."""

    error_code: str
    message: str
    details: Optional[dict] = None


class PaginatedResponse(BaseModel):
    """Generic paginated response."""

    items: List[dict] = Field(default_factory=list)
    total: int
    page: int
    page_size: int
    has_next: bool


# ============ Enums ============

class ComplianceIssueSeverity(str, Enum):
    """Severity levels for compliance issues."""

    CRITICAL = "critical"
    WARNING = "warning"
    SUGGESTION = "suggestion"


class ComplianceIssueType(str, Enum):
    """Types of compliance issues."""

    PAGE_LIMIT = "page_limit"
    ANONYMITY = "anonymity"
    REFERENCE_FORMAT = "reference_format"
    TEMPLATE = "template"
    MARGIN = "margin"
    MISSING_SECTION = "missing_section"
    CLAIMS_INTEGRITY = "claims_integrity"


class ConferenceType(str, Enum):
    """Conference categories."""

    ACADEMIC = "academic"
    INDUSTRY = "industry"
    NLP = "nlp"
    VISION = "vision"
    DATA = "data"
    WORKSHOP = "workshop"


class PaperStatus(str, Enum):
    """Status of a paper in the system."""

    DRAFT = "draft"
    UPLOADED = "uploaded"
    PARSING = "parsing"
    ANALYZED = "analyzed"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"
    ERROR = "error"


class ReportStatus(str, Enum):
    """Status of a compliance report."""

    DRAFT = "draft"
    REVIEWED = "reviewed"
    RESOLVED = "resolved"


# ============ Conference Schemas ============

class ConferenceBrief(BaseModel):
    """Minimal conference info for listing."""

    id: str
    abbr: str
    name: str
    start_date: date
    submission_deadline: date
    location: str
    flag: str
    conference_type: ConferenceType
    topics: List[str]
    description: Optional[str] = None


class ConferenceGuidelines(BaseModel):
    """Conference submission guidelines."""

    conference_id: str
    max_pages: int
    min_pages: Optional[int] = None
    requires_anonymity: bool
    reference_format: str  # e.g., "bibtex", "ieee", "acm"
    margin_top_cm: float
    margin_bottom_cm: float
    margin_left_cm: float
    margin_right_cm: float
    required_sections: List[str] = Field(default_factory=list)
    forbidden_topics: List[str] = Field(default_factory=list)
    special_rules: List[str] = Field(default_factory=list)
    notes: str = Field(default="TODO: Verify with official guidelines")


class ConferenceDetailed(ConferenceBrief):
    """Full conference with guidelines."""

    url: HttpUrl
    guidelines: ConferenceGuidelines
    notification_date: Optional[date] = None
    acceptance_rate: Optional[float] = None


class ConferenceFilter(BaseModel):
    """Filter parameters for conference listing."""

    search_query: Optional[str] = None
    conference_types: Optional[List[str]] = None
    topics: Optional[List[str]] = None
    deadline_within_days: Optional[int] = None


# ============ Paper Schemas ============

class PaperMetadata(BaseModel):
    """Extracted paper metadata."""

    paper_id: str
    title: str
    authors: List[str] = Field(default_factory=list)
    abstract: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    conference_id: str
    upload_date: datetime


class PaperCreate(BaseModel):
    """Schema for creating a new paper."""

    conference_id: str
    title: str
    authors: List[str] = Field(default_factory=list)
    abstract: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)


class PaperRead(BaseModel):
    """Paper data for API responses."""

    id: str
    conference_id: str
    title: str
    authors: List[str]
    abstract: Optional[str] = None
    keywords: List[str]
    status: str
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    upload_date: datetime
    last_modified: datetime


# ============ Compliance Schemas ============

class ComplianceIssue(BaseModel):
    """Single compliance issue."""

    id: str
    issue_type: ComplianceIssueType
    severity: ComplianceIssueSeverity
    title: str
    description: str
    guideline_reference: str
    suggested_fix: str
    paper_location: Optional[str] = None  # e.g., "Page 3, Line 15"
    detected_by: str  # Checker or Agent name
    resolved: bool = False


class ComplianceReportSummary(BaseModel):
    """Summary statistics for compliance report."""

    total_issues: int
    critical_count: int
    warning_count: int
    suggestion_count: int
    resolved_count: int
    compliance_score: float  # 0-100


class ComplianceReport(BaseModel):
    """Full compliance report for a paper."""

    id: str
    paper_id: str
    conference_id: str
    generated_at: datetime
    issues: List[ComplianceIssue] = Field(default_factory=list)
    summary: ComplianceReportSummary
    status: ReportStatus


# ============ Generation Schemas ============

class PackageGenerationStatus(BaseModel):
    """Status of package generation."""

    id: str
    paper_id: str
    status: str  # "queued", "generating", "completed", "failed"
    progress_percent: int = 0
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    package_url: Optional[HttpUrl] = None
    package_size_bytes: Optional[int] = None


# ============ Phase 3: Upload & Compliance Schemas ============

class PaperUploadResponse(BaseModel):
    """Response after paper upload."""

    paper_id: str
    file_name: str
    file_type: str
    file_size: int
    storage_path: str
    upload_status: str


class ParsedPaper(BaseModel):
    """Parsed paper data."""

    paper_id: str
    file_type: str
    page_count: Optional[int] = None
    title: Optional[str] = None
    abstract_found: bool
    references_found: bool
    citation_patterns_found: bool
    sections: List[str] = Field(default_factory=list)
    extracted_text: Optional[str] = None


class ComplianceAnalyzeRequest(BaseModel):
    """Request to analyze paper compliance."""

    paper_id: str
    conference_id: str


class ComplianceIssueDetail(BaseModel):
    """Single compliance issue."""

    issue_id: str
    category: str
    severity: str
    message: str
    location: Optional[str] = None
    suggested_fix: Optional[str] = None
    needs_verification: bool


class ComplianceReportResponse(BaseModel):
    """Compliance analysis report response."""

    project_id: Optional[str] = None
    paper_id: str
    conference_id: str
    overall_status: str
    readiness_score: int
    issues: List[ComplianceIssueDetail] = Field(default_factory=list)
    passed_checks: List[str] = Field(default_factory=list)
    warnings_count: int
    critical_count: int


# ============ Phase 4: Compliance Report & Package Generation Schemas ============

class ComplianceSummary(BaseModel):
    """Summary statistics for compliance report."""

    total_checks: int
    passed_count: int
    warning_count: int
    critical_count: int
    info_count: int


class FixSuggestion(BaseModel):
    """Fix suggestion for compliance issue."""

    issue_id: str
    can_auto_fix: bool
    suggested_action: str
    replacement_text: Optional[str] = None
    explanation: str


class ComplianceReport(BaseModel):
    """Complete compliance report."""

    project_id: str
    paper_id: str
    conference_id: str
    overall_status: str
    readiness_score: int
    summary: ComplianceSummary
    issues: List[ComplianceIssueDetail] = Field(default_factory=list)
    fix_suggestions: List[FixSuggestion] = Field(default_factory=list)
    passed_checks: List[str] = Field(default_factory=list)
    generated_at: str


class PackageGenerationRequest(BaseModel):
    """Request to generate Overleaf package."""

    paper_id: str
    conference_id: str
    project_id: Optional[str] = None
    package_type: str = "neurips_overleaf"


class GeneratedFile(BaseModel):
    """Metadata for a generated file."""

    file_name: str
    file_type: str
    file_path: str


class PackageGenerationResponse(BaseModel):
    """Response from package generation."""

    package_id: str
    project_id: Optional[str] = None
    paper_id: str
    conference_id: str
    package_type: str
    zip_file_path: str
    generated_files: List[GeneratedFile] = Field(default_factory=list)
    status: str
    message: str
