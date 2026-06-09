"""Generation service."""

from sqlalchemy.orm import Session
from ..core import get_logger

logger = get_logger(__name__)


class GenerationService:
    """Service for package generation."""

    def __init__(self, db: Session):
        """Initialize service."""
        self.db = db

    async def generate_package(self, paper_id: str, conference_id: str, include_metadata: bool = True, include_report: bool = True):
        """
        Generate Overleaf-ready LaTeX package.
        
        TODO: Orchestrate generators
        """
        logger.info(f"Generating package: paper={paper_id}, conference={conference_id}")
        # TODO: Load paper
        # TODO: Load compliance report (if include_report)
        # TODO: Load guidelines
        # TODO: Generate main.tex
        # TODO: Generate references.bib
        # TODO: Generate metadata.json (if include_metadata)
        # TODO: Create ZIP file
        # TODO: Save to storage
        # TODO: Return status

    async def get_generation_status(self, paper_id: str):
        """
        Get package generation status.
        
        TODO: Implement status check
        """
        logger.info(f"Getting generation status: {paper_id}")
        # TODO: Query database
        # TODO: Return status
