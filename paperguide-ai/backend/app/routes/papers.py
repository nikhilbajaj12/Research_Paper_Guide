"""Paper management routes."""

import os
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, Query, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..services import PaperService
from ..schemas import PaperCreate, PaperMetadata, PaperStatus
from ..core import get_logger, NotFoundError, settings

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/papers", tags=["papers"])


@router.post("", response_model=dict)
async def create_paper(
    paper: PaperCreate,
    project_id: str = Query(None),
    db: Session = Depends(get_db),
):
    """
    Create a new paper record.
    
    Request Body:
    - conference_id: Target conference ID
    - title: Paper title
    - authors: List of author names
    - abstract: Paper abstract
    - keywords: List of keywords
    
    Query Parameters:
    - project_id: Optional project ID to associate with paper
    
    Returns:
        Created paper with ID
    """
    logger.info(f"POST /papers - Creating paper for conference: {paper.conference_id}")
    try:
        service = PaperService(db)
        result = await service.create_paper(paper, project_id=project_id)
        logger.info(f"Paper created: {result['id']}")
        return result
    except Exception as e:
        logger.error(f"Error creating paper: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create paper")


@router.get("/{paper_id}", response_model=dict)
async def get_paper(
    paper_id: str,
    db: Session = Depends(get_db),
):
    """
    Get paper details and metadata.
    
    Path Parameters:
    - paper_id: Paper ID
    
    Returns:
        Paper details
    """
    logger.info(f"GET /papers/{paper_id}")
    try:
        service = PaperService(db)
        paper = await service.get_paper_by_id(paper_id)
        logger.info(f"Retrieved paper: {paper_id}")
        return paper
    except NotFoundError:
        logger.warning(f"Paper not found: {paper_id}")
        raise HTTPException(status_code=404, detail=f"Paper '{paper_id}' not found")
    except Exception as e:
        logger.error(f"Error retrieving paper {paper_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve paper")


@router.get("/{paper_id}/metadata", response_model=PaperMetadata)
async def get_paper_metadata(
    paper_id: str,
    db: Session = Depends(get_db),
):
    """
    Get paper metadata only.
    
    Path Parameters:
    - paper_id: Paper ID
    
    Returns:
        Paper metadata
    """
    logger.info(f"GET /papers/{paper_id}/metadata")
    try:
        service = PaperService(db)
        metadata = await service.get_paper_metadata(paper_id)
        logger.info(f"Retrieved metadata for: {paper_id}")
        return metadata
    except NotFoundError:
        logger.warning(f"Paper not found: {paper_id}")
        raise HTTPException(status_code=404, detail=f"Paper '{paper_id}' not found")
    except Exception as e:
        logger.error(f"Error retrieving metadata for {paper_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve metadata")


@router.put("/{paper_id}/status", response_model=dict)
async def update_paper_status(
    paper_id: str,
    status: str = Query(..., description="New status"),
    db: Session = Depends(get_db),
):
    """
    Update paper status.
    
    Path Parameters:
    - paper_id: Paper ID
    
    Query Parameters:
    - status: New status (draft, submitted, under_review, accepted, rejected)
    
    Returns:
        Updated paper data
    """
    logger.info(f"PUT /papers/{paper_id}/status - status={status}")
    try:
        service = PaperService(db)
        result = await service.update_paper_status(paper_id, status)
        logger.info(f"Paper {paper_id} status updated to: {status}")
        return result
    except NotFoundError:
        logger.warning(f"Paper not found: {paper_id}")
        raise HTTPException(status_code=404, detail=f"Paper '{paper_id}' not found")
    except Exception as e:
        logger.error(f"Error updating paper status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update paper status")


@router.delete("/{paper_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_paper(
    paper_id: str,
    db: Session = Depends(get_db),
):
    """
    Delete a paper and associated files.
    
    Path Parameters:
    - paper_id: Paper ID
    
    Returns:
        204 No Content
    """
    logger.info(f"DELETE /papers/{paper_id}")
    try:
        service = PaperService(db)
        await service.delete_paper(paper_id)
        logger.info(f"Paper deleted: {paper_id}")
    except NotFoundError:
        logger.warning(f"Paper not found: {paper_id}")
        raise HTTPException(status_code=404, detail=f"Paper '{paper_id}' not found")
    except Exception as e:
        logger.error(f"Error deleting paper {paper_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete paper")


@router.get("/list/conference/{conference_id}", response_model=list[dict])
async def list_papers_by_conference(
    conference_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """
    List papers for a conference.
    
    Path Parameters:
    - conference_id: Conference ID
    
    Query Parameters:
    - skip: Number of records to skip
    - limit: Maximum records to return
    
    Returns:
        List of papers
    """
    logger.info(f"GET /papers/list/conference/{conference_id}")
    try:
        service = PaperService(db)
        papers = await service.list_papers_by_conference(conference_id, skip=skip, limit=limit)
        logger.info(f"Retrieved {len(papers)} papers for conference: {conference_id}")
        return papers
    except Exception as e:
        logger.error(f"Error listing papers for conference {conference_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve papers")
