"""Conference management routes."""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..services import ConferenceService
from ..schemas import ConferenceBrief, ConferenceDetailed, ConferenceGuidelines
from ..conference import config_loader
from ..core import get_logger, NotFoundError

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/conferences", tags=["conferences"])


@router.get("", response_model=list[ConferenceBrief])
async def list_conferences(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """
    Get all conferences with pagination.
    
    Query Parameters:
    - skip: Number of records to skip (default: 0)
    - limit: Maximum records to return (default: 100, max: 1000)
    
    Returns:
        List of conferences
    """
    logger.info(f"GET /conferences - skip={skip}, limit={limit}")
    try:
        service = ConferenceService(db)
        conferences = await service.get_all_conferences(skip=skip, limit=limit)
        logger.info(f"Retrieved {len(conferences)} conferences")
        return conferences
    except Exception as e:
        logger.error(f"Error retrieving conferences: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve conferences")


@router.get("/search", response_model=list[ConferenceBrief])
async def search_conferences(
    search: str = Query(None, min_length=1, description="Search term"),
    types: list[str] = Query(None, description="Filter by conference types"),
    topics: list[str] = Query(None, description="Filter by topics"),
    deadline_within_days: int = Query(None, ge=1, description="Deadline within N days"),
    db: Session = Depends(get_db),
):
    """
    Search and filter conferences.
    
    Query Parameters:
    - search: Search in name, location, abbreviation
    - types: Filter by conference types (e.g., 'top_tier', 'workshop')
    - topics: Filter by topics (e.g., 'AI', 'ML')
    - deadline_within_days: Show conferences with deadline within N days
    
    Returns:
        Filtered list of conferences
    """
    logger.info(f"GET /search - search={search}, types={types}, topics={topics}")
    try:
        service = ConferenceService(db)
        conferences = await service.filter_conferences(
            search=search,
            conference_types=types,
            topics=topics,
            deadline_within_days=deadline_within_days,
        )
        logger.info(f"Search returned {len(conferences)} conferences")
        return conferences
    except Exception as e:
        logger.error(f"Error searching conferences: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search conferences")


@router.get("/{conference_id}", response_model=ConferenceDetailed)
async def get_conference(
    conference_id: str,
    db: Session = Depends(get_db),
):
    """
    Get conference details including guidelines.
    
    Path Parameters:
    - conference_id: Conference identifier (e.g., 'neurips_2025')
    
    Returns:
        Conference details with guidelines
    """
    logger.info(f"GET /conferences/{conference_id}")
    try:
        service = ConferenceService(db)
        conference = await service.get_conference_by_id(conference_id)
        logger.info(f"Retrieved conference: {conference_id}")
        return conference
    except NotFoundError:
        logger.warning(f"Conference not found: {conference_id}")
        raise HTTPException(status_code=404, detail=f"Conference '{conference_id}' not found")
    except Exception as e:
        logger.error(f"Error retrieving conference {conference_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve conference")


@router.get("/{conference_id}/guidelines", response_model=ConferenceGuidelines)
async def get_guidelines(
    conference_id: str,
    db: Session = Depends(get_db),
):
    """
    Get submission guidelines for a conference.
    
    Path Parameters:
    - conference_id: Conference identifier
    
    Returns:
        Conference guidelines
    """
    logger.info(f"GET /conferences/{conference_id}/guidelines")
    try:
        service = ConferenceService(db)
        guidelines = await service.get_guidelines(conference_id)
        logger.info(f"Retrieved guidelines for: {conference_id}")
        return guidelines
    except NotFoundError:
        logger.warning(f"Guidelines not found for: {conference_id}")
        raise HTTPException(status_code=404, detail=f"Guidelines for '{conference_id}' not found")
    except Exception as e:
        logger.error(f"Error retrieving guidelines for {conference_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve guidelines")


@router.get("/configs/list", response_model=list[dict])
async def list_configs():
    """List all available conference configs (from JSON files, not DB)."""
    return config_loader.list_available()


@router.get("/configs/{conference_id}/validate")
async def validate_config(conference_id: str):
    """Validate a conference config file."""
    return config_loader.validate_config(conference_id)


@router.post("/configs/reload")
async def reload_configs():
    """Clear config cache and force-reload all configs."""
    config_loader.clear_cache()
    available = config_loader.list_available()
    return {"status": "ok", "configs_reloaded": len(available), "available": available}
