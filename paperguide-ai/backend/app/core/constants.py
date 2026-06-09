"""Application constants and magic numbers."""

# NeurIPS 2025/2026 Guidelines (MVP)
NEURIPS_2025_ID = "neurips-2025"
NEURIPS_2025_MAX_PAGES = 9
NEURIPS_2025_REQUIRES_ANONYMITY = True
NEURIPS_2025_REFERENCE_FORMAT = "bibtex"
NEURIPS_2025_SUBMISSION_DEADLINE = "2025-09-30"
NEURIPS_2025_NOTIFICATION_DATE = "2025-11-01"
NEURIPS_2025_CONFERENCE_DATES = ("2025-12-02", "2025-12-07")

# Page/File Limits
MAX_PDF_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB
MIN_PDF_SIZE_BYTES = 1 * 1024  # 1 KB
MAX_PAGES_REASONABLE = 100  # Sanity check

# Paper Structure
EXPECTED_SECTIONS = [
    "abstract",
    "introduction",
    "related work",
    "method",
    "experiments",
    "results",
    "discussion",
    "references",
]

# Compliance Issue Severity Levels
ISSUE_SEVERITY_CRITICAL = "critical"
ISSUE_SEVERITY_WARNING = "warning"
ISSUE_SEVERITY_SUGGESTION = "suggestion"

# Compliance Issue Types
ISSUE_TYPE_PAGE_LIMIT = "page_limit"
ISSUE_TYPE_ANONYMITY = "anonymity"
ISSUE_TYPE_REFERENCE_FORMAT = "reference_format"
ISSUE_TYPE_TEMPLATE = "template"
ISSUE_TYPE_MARGIN = "margin"
ISSUE_TYPE_MISSING_SECTION = "missing_section"
ISSUE_TYPE_CLAIMS_INTEGRITY = "claims_integrity"

# Compliance Score Thresholds
COMPLIANCE_SCORE_CRITICAL = 50  # Below this = many critical issues
COMPLIANCE_SCORE_WARNING = 75  # Below this = some issues
COMPLIANCE_SCORE_GOOD = 90  # Above this = minor issues only

# Timeout Settings (seconds)
PDF_PARSE_TIMEOUT = 30
COMPLIANCE_ANALYSIS_TIMEOUT = 120

# TODO: NeurIPS guidelines verification
# - Max pages: 9 (+ unlimited references and appendices)
# - Anonymity: Author names, affiliations must be removed
# - Reference format: BibTeX
# - Citation style: NeurIPS (numbered [1], [2], etc.)
# - Margins: 1 inch on all sides
# - Font: 10pt or larger
# - Figure/Table captions: numbered and descriptive
