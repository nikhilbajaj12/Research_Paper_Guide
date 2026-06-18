"""Phase 2 auto-fix pipeline schemas."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class FixStep(BaseModel):
    """A single step in the execution plan."""
    step_id: str
    agent: str
    action: str
    target: str
    details: str = ""
    status: str = "pending"  # pending | running | completed | failed


class ExecutionPlan(BaseModel):
    """Plan produced by the Planner Agent."""
    plan_id: str
    steps: List[FixStep] = Field(default_factory=list)
    summary: str = ""


class AgentResult(BaseModel):
    """Result from a single fix agent."""
    agent: str
    success: bool
    changes_made: List[str] = Field(default_factory=list)
    error: Optional[str] = None


class BeforeAfterScore(BaseModel):
    """Before/after compliance score comparison."""
    before_score: int
    after_score: int
    improvement: int
    before_status: str
    after_status: str


class FixPipelineResult(BaseModel):
    """Final result of the fix pipeline."""
    plan: ExecutionPlan
    agent_results: List[AgentResult] = Field(default_factory=list)
    score_comparison: Optional[BeforeAfterScore] = None
    package_path: Optional[str] = None
    package_download_url: Optional[str] = None
    fixed_file_path: Optional[str] = None
    audit_log: List[Dict[str, Any]] = Field(default_factory=list)
    success: bool = False
    error: Optional[str] = None


class AutoFixRequest(BaseModel):
    """Request to start auto-fix pipeline."""
    paper_id: str
    conference_id: str
    command: str = "Fix all issues"
    steps: Optional[List[str]] = None  # optional override: which agents to run


class AutoFixStatusResponse(BaseModel):
    """Status of a running/finished fix pipeline."""
    pipeline_id: str
    status: str  # running | completed | failed
    progress: int = 0  # 0-100
    result: Optional[FixPipelineResult] = None
    error: Optional[str] = None


class DocumentEditRequest(BaseModel):
    """Request to edit a document."""
    paper_id: str
    edits: List[Dict[str, Any]] = Field(default_factory=list)


class DocumentEditResponse(BaseModel):
    """Response after editing a document."""
    success: bool
    original_backup: str
    edited_path: str
    changes: List[str] = Field(default_factory=list)
