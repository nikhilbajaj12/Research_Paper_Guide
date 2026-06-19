"""Pydantic schemas for the API."""

import base64
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
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


class RecommendationDetail(BaseModel):
    """Actionable recommendation for fixing a compliance issue."""

    issue: str
    location: str
    severity: str
    suggested_action: str
    explanation: str
    category: str = ""
    can_auto_fix: bool = False


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
    recommendations: List[RecommendationDetail] = Field(default_factory=list)


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


# ============ AI Assistant Schemas ============

class AssistantChatRequest(BaseModel):
    """Request to chat with the AI Assistant."""

    conference: Optional[Dict[str, Any]] = None
    compliance_score: int = 0
    critical_issues: List[Dict[str, Any]] = Field(default_factory=list)
    warnings: List[Dict[str, Any]] = Field(default_factory=list)
    passed_checks: List[str] = Field(default_factory=list)
    recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    user_message: str = ""
    paper_id: Optional[str] = None
    conference_id: Optional[str] = None


class AssistantChatResponse(BaseModel):
    """Response from the AI Assistant."""

    answer: str
    fix_run: bool = False
    pipeline_id: Optional[str] = None
    download_url: Optional[str] = None
    fix_summary: Optional[str] = None


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


# ============ Architecture V2 Dataclasses ============

@dataclass
class ParsedDocument:
    """Standardized parsed document reused across all stages."""

    paper_id: str
    file_type: str
    title: Optional[str] = None
    abstract: Optional[str] = None
    authors: List[str] = field(default_factory=list)
    sections: List[str] = field(default_factory=list)
    page_count: Optional[int] = None
    references_found: bool = False
    citation_patterns_found: bool = False
    citation_patterns: List[str] = field(default_factory=list)
    numeric_claims: List[Dict[str, Any]] = field(default_factory=list)
    extracted_text: Optional[str] = None
    source_files: Dict[str, bytes] = field(default_factory=dict)
    main_tex_content: Optional[str] = None
    bib_files: List[str] = field(default_factory=list)
    sty_files: List[str] = field(default_factory=list)
    abstract_found: bool = False
    has_checklist: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    def __getitem__(self, key: str) -> Any:
        """Allow dict-style access for backward compat with existing checkers."""
        return getattr(self, key)

    def get(self, key: str, default: Any = None) -> Any:
        """Dict-style .get() for backward compat."""
        return getattr(self, key, default)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict for cache storage."""
        result = {}
        for k, v in self.__dict__.items():
            if k == "source_files":
                result[k] = {name: base64.b64encode(content).decode() for name, content in v.items()}
            else:
                result[k] = v
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ParsedDocument":
        """Deserialize from dict."""
        data = dict(data)
        if "source_files" in data and data["source_files"]:
            data["source_files"] = {
                name: base64.b64decode(content.encode()) if isinstance(content, str) else content
                for name, content in data["source_files"].items()
            }
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class ValidationResult:
    """Result from a single validation check."""

    status: str  # "pass" | "warning" | "critical"
    issue: str
    location: str
    recommendation: str
    category: str
    needs_verification: bool = False

    def to_issue_dict(self) -> Dict[str, Any]:
        """Convert to the ComplianceIssueDetail format expected by the API."""
        return {
            "issue_id": f"{self.category}_{hash(self.issue) & 0xFFFF}",
            "category": self.category,
            "severity": self.status,
            "message": self.issue,
            "location": self.location,
            "suggested_fix": self.recommendation,
            "needs_verification": self.needs_verification,
        }


@dataclass
class ScoreResult:
    """Result from the scoring engine."""

    score: int
    status: str
    critical_count: int = 0
    warnings_count: int = 0
    info_count: int = 0


@dataclass
class Recommendation:
    """Actionable recommendation for fixing an issue."""

    issue_id: str
    category: str
    can_auto_fix: bool
    suggested_action: str
    issue: str = ""
    location: str = ""
    severity: str = ""
    replacement_text: Optional[str] = None
    explanation: str = ""


@dataclass
class ConferenceConfig:
    """Conference configuration loaded from JSON files."""

    conference_id: str
    conference_name: str
    conference_year: int = 2026
    max_pages: int = 9
    min_pages: int = 1
    blind_review: bool = True
    reference_style: str = "bibtex"
    required_sections: List[str] = field(default_factory=list)
    optional_sections: List[str] = field(default_factory=list)
    required_keywords: List[str] = field(default_factory=list)
    margin_rules: Dict[str, float] = field(default_factory=lambda: {"top_cm": 2.54, "bottom_cm": 2.54, "left_cm": 2.54, "right_cm": 2.54})
    package_template: str = ""
    scoring_weights: Dict[str, int] = field(default_factory=lambda: {"critical": 20, "warning": 8, "info": 2})
    allowed_file_types: List[str] = field(default_factory=lambda: [".pdf", ".docx", ".zip"])
    forbidden_topics: List[str] = field(default_factory=list)
    special_rules: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConferenceConfig":
        """Create from dict (JSON config file)."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def to_guidelines_dict(self) -> Dict[str, Any]:
        """Return a flat dict compatible with existing validators (guidelines format)."""
        return {
            "conference_id": self.conference_id,
            "max_pages": self.max_pages,
            "min_pages": self.min_pages,
            "requires_anonymity": self.blind_review,
            "reference_format": self.reference_style,
            "required_sections": list(self.required_sections),
            "margin_top_cm": self.margin_rules.get("top_cm", 2.54),
            "margin_bottom_cm": self.margin_rules.get("bottom_cm", 2.54),
            "margin_left_cm": self.margin_rules.get("left_cm", 2.54),
            "margin_right_cm": self.margin_rules.get("right_cm", 2.54),
            "forbidden_topics": list(self.forbidden_topics),
            "special_rules": list(self.special_rules),
            "package_template": self.package_template,
        }
