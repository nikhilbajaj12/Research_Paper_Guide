"""Project/submission history routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import PaperRead
from ..core import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("")
async def list_projects(
    conference_id: str = Query(None),
    status: str = Query(None),
    sort: str = Query("date"),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    List user's projects/submissions.
    
    Query Parameters:
    - conference_id: Filter by conference
    - status: Filter by status (draft, submitted, accepted, rejected)
    - sort: Sort by 'date' or 'name'
    - limit: Number of results (1-100)
    
    Returns: List of projects
    
    TODO: Implement listing with filters
    """
    logger.info(f"Listing projects with filters: conference={conference_id}, status={status}")
    # TODO: Query database with filters
    # TODO: Sort results
    # TODO: Return list


@router.get("/{project_id}")
async def get_project(project_id: str, db: Session = Depends(get_db)):
    """
    Get project details.
    
    Path Parameters:
    - project_id: Project ID
    
    Returns: Project details
    
    TODO: Implement retrieval logic
    """
    logger.info(f"Getting project: {project_id}")
    # TODO: Query database
    # TODO: Return project
    # TODO: Handle not found error


@router.post("/{project_id}/resubmit", response_model=PaperRead)
async def resubmit_paper(
    project_id: str,
    target_conference_id: str,
    db: Session = Depends(get_db),
):
    """
    Create new project from existing paper for different conference.
    
    Path Parameters:
    - project_id: Original project ID
    
    Query Parameters:
    - target_conference_id: New target conference ID
    
    Returns: New PaperRead object
    
    TODO: Implement resubmission logic
    """
    logger.info(f"Resubmitting paper from project {project_id} to conference {target_conference_id}")
    # TODO: Load original project
    # TODO: Create new project with same paper
    # TODO: Set new conference
    # TODO: Return new project
    # TODO: Handle not found errors
