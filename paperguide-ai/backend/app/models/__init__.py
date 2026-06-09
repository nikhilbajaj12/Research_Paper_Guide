"""SQLAlchemy ORM models for database."""

from sqlalchemy import Column, String, Integer, DateTime, Text, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Conference(Base):
    """Conference database model."""

    __tablename__ = "conferences"

    id = Column(String, primary_key=True)
    abbr = Column(String, index=True)
    name = Column(String, index=True)
    start_date = Column(String)  # ISO format
    end_date = Column(String)  # ISO format
    submission_deadline = Column(String)
    notification_date = Column(String, nullable=True)
    location = Column(String)
    flag = Column(String)
    conference_type = Column(String)  # academic, industry, nlp, vision, data
    topics = Column(JSON, default=[])
    description = Column(Text, nullable=True)
    url = Column(String, nullable=True)
    acceptance_rate = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        """String representation."""
        return f"<Conference {self.abbr}>"


class ConferenceGuidelines(Base):
    """Conference guidelines database model."""

    __tablename__ = "conference_guidelines"

    id = Column(String, primary_key=True)
    conference_id = Column(String, index=True)
    max_pages = Column(Integer)
    min_pages = Column(Integer, nullable=True)
    requires_anonymity = Column(Boolean, default=True)
    reference_format = Column(String)  # bibtex, ieee, acm
    margin_top_cm = Column(Float)
    margin_bottom_cm = Column(Float)
    margin_left_cm = Column(Float)
    margin_right_cm = Column(Float)
    required_sections = Column(JSON, default=[])
    forbidden_topics = Column(JSON, default=[])
    special_rules = Column(JSON, default=[])
    notes = Column(Text, default="TODO: Verify with official guidelines")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        """String representation."""
        return f"<ConferenceGuidelines {self.conference_id}>"


class Paper(Base):
    """Paper database model."""

    __tablename__ = "papers"

    id = Column(String, primary_key=True)
    conference_id = Column(String, index=True)
    original_filename = Column(String)
    storage_path = Column(String)
    title = Column(String, nullable=True)
    authors = Column(JSON, default=[])
    abstract = Column(Text, nullable=True)
    page_count = Column(Integer, nullable=True)
    word_count = Column(Integer, nullable=True)
    citation_count = Column(Integer, nullable=True)
    section_structure = Column(JSON, default={})
    figure_count = Column(Integer, default=0)
    table_count = Column(Integer, default=0)
    status = Column(String, default="uploaded")  # uploaded, parsing, analyzed, completed
    current_report_id = Column(String, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    last_analyzed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        """String representation."""
        return f"<Paper {self.id}>"


class ComplianceIssue(Base):
    """Compliance issue database model."""

    __tablename__ = "compliance_issues"

    id = Column(String, primary_key=True)
    report_id = Column(String, index=True)
    paper_id = Column(String, index=True)
    issue_type = Column(String)  # page_limit, anonymity, reference_format, etc.
    severity = Column(String)  # critical, warning, suggestion
    title = Column(String)
    description = Column(Text)
    guideline_reference = Column(String)
    suggested_fix = Column(Text)
    paper_location = Column(String, nullable=True)  # Page 3, Line 15
    detected_by = Column(String)  # Checker or Agent name
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        """String representation."""
        return f"<ComplianceIssue {self.id}>"


class ComplianceReport(Base):
    """Compliance report database model."""

    __tablename__ = "compliance_reports"

    id = Column(String, primary_key=True)
    paper_id = Column(String, index=True)
    conference_id = Column(String, index=True)
    total_issues = Column(Integer, default=0)
    critical_count = Column(Integer, default=0)
    warning_count = Column(Integer, default=0)
    suggestion_count = Column(Integer, default=0)
    resolved_count = Column(Integer, default=0)
    compliance_score = Column(Float, default=0.0)  # 0-100
    status = Column(String, default="draft")  # draft, reviewed, resolved
    generated_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        """String representation."""
        return f"<ComplianceReport {self.id}>"


class Project(Base):
    """Project/submission database model."""

    __tablename__ = "projects"

    id = Column(String, primary_key=True)
    paper_id = Column(String, index=True)
    conference_id = Column(String, index=True)
    status = Column(String)  # draft, submitted, accepted, rejected
    current_report_id = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        """String representation."""
        return f"<Project {self.id}>"
