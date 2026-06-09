"""Paper service."""

import os
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from ..models import Paper as PaperModel, Project as ProjectModel
from ..schemas import PaperMetadata, PaperCreate, PaperStatus
from ..core import get_logger, NotFoundError, settings
import shutil

logger = get_logger(__name__)


class PaperService:
    """Service for paper operations."""

    def __init__(self, db: Session):
        """Initialize service."""
        self.db = db

    async def create_paper(self, paper_data: PaperCreate, project_id: str = None) -> dict:
        """
        Create new paper record.
        
        Args:
            paper_data: Paper metadata
            project_id: Optional project association
            
        Returns:
            Created paper data with ID
        """
        logger.info(f"Creating paper for conference: {paper_data.conference_id}")
        
        paper_id = str(uuid.uuid4())
        
        paper = PaperModel(
            id=paper_id,
            project_id=project_id,
            conference_id=paper_data.conference_id,
            title=paper_data.title,
            authors=paper_data.authors,
            abstract=paper_data.abstract,
            keywords=paper_data.keywords,
            status=PaperStatus.DRAFT,
            file_path=None,
            file_size=None,
            upload_date=datetime.utcnow(),
            last_modified=datetime.utcnow(),
        )
        
        self.db.add(paper)
        self.db.commit()
        self.db.refresh(paper)
        
        logger.info(f"Paper created with ID: {paper_id}")
        
        return {
            "id": paper.id,
            "conference_id": paper.conference_id,
            "title": paper.title,
            "status": paper.status,
            "upload_date": paper.upload_date,
        }

    async def get_paper_by_id(self, paper_id: str) -> dict:
        """
        Get paper by ID.
        
        Args:
            paper_id: Paper ID
            
        Returns:
            Paper data
            
        Raises:
            NotFoundError: If paper not found
        """
        logger.info(f"Getting paper: {paper_id}")
        
        paper = self.db.query(PaperModel).filter(PaperModel.id == paper_id).first()
        
        if not paper:
            logger.warning(f"Paper not found: {paper_id}")
            raise NotFoundError("Paper", paper_id)
        
        return {
            "id": paper.id,
            "project_id": paper.project_id,
            "conference_id": paper.conference_id,
            "title": paper.title,
            "authors": paper.authors,
            "abstract": paper.abstract,
            "keywords": paper.keywords,
            "status": paper.status,
            "file_path": paper.file_path,
            "file_size": paper.file_size,
            "upload_date": paper.upload_date,
            "last_modified": paper.last_modified,
        }

    async def get_papers_by_project(self, project_id: str) -> list[dict]:
        """
        Get all papers in a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            List of papers
        """
        logger.info(f"Getting papers for project: {project_id}")
        
        papers = self.db.query(PaperModel).filter(
            PaperModel.project_id == project_id
        ).all()
        
        result = []
        for paper in papers:
            result.append({
                "id": paper.id,
                "conference_id": paper.conference_id,
                "title": paper.title,
                "status": paper.status,
                "upload_date": paper.upload_date,
            })
        
        return result

    async def get_paper_metadata(self, paper_id: str) -> PaperMetadata:
        """
        Get paper metadata.
        
        Args:
            paper_id: Paper ID
            
        Returns:
            Paper metadata
            
        Raises:
            NotFoundError: If paper not found
        """
        logger.info(f"Getting metadata for paper: {paper_id}")
        
        paper = self.db.query(PaperModel).filter(PaperModel.id == paper_id).first()
        
        if not paper:
            logger.warning(f"Paper not found: {paper_id}")
            raise NotFoundError("Paper", paper_id)
        
        return PaperMetadata(
            paper_id=paper.id,
            title=paper.title,
            authors=paper.authors,
            abstract=paper.abstract,
            keywords=paper.keywords,
            conference_id=paper.conference_id,
            upload_date=paper.upload_date,
        )

    async def update_paper_status(self, paper_id: str, status: str) -> dict:
        """
        Update paper status.
        
        Args:
            paper_id: Paper ID
            status: New status
            
        Returns:
            Updated paper data
            
        Raises:
            NotFoundError: If paper not found
        """
        logger.info(f"Updating paper {paper_id} status to: {status}")
        
        paper = self.db.query(PaperModel).filter(PaperModel.id == paper_id).first()
        
        if not paper:
            logger.warning(f"Paper not found: {paper_id}")
            raise NotFoundError("Paper", paper_id)
        
        paper.status = status
        paper.last_modified = datetime.utcnow()
        self.db.commit()
        self.db.refresh(paper)
        
        logger.info(f"Paper {paper_id} status updated")
        
        return {
            "id": paper.id,
            "status": paper.status,
            "last_modified": paper.last_modified,
        }

    async def delete_paper(self, paper_id: str) -> bool:
        """
        Delete paper and associated files.
        
        Args:
            paper_id: Paper ID
            
        Returns:
            True if deleted, False otherwise
            
        Raises:
            NotFoundError: If paper not found
        """
        logger.info(f"Deleting paper: {paper_id}")
        
        paper = self.db.query(PaperModel).filter(PaperModel.id == paper_id).first()
        
        if not paper:
            logger.warning(f"Paper not found: {paper_id}")
            raise NotFoundError("Paper", paper_id)
        
        # Delete file if it exists
        if paper.file_path and os.path.exists(paper.file_path):
            try:
                os.remove(paper.file_path)
                logger.info(f"Deleted file: {paper.file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete file {paper.file_path}: {str(e)}")
        
        # Delete from database
        self.db.delete(paper)
        self.db.commit()
        
        logger.info(f"Paper {paper_id} deleted")
        
        return True

    async def get_paper_file_info(self, paper_id: str) -> dict:
        """
        Get paper file information.
        
        Args:
            paper_id: Paper ID
            
        Returns:
            File information
            
        Raises:
            NotFoundError: If paper or file not found
        """
        logger.info(f"Getting file info for paper: {paper_id}")
        
        paper = self.db.query(PaperModel).filter(PaperModel.id == paper_id).first()
        
        if not paper:
            logger.warning(f"Paper not found: {paper_id}")
            raise NotFoundError("Paper", paper_id)
        
        if not paper.file_path or not os.path.exists(paper.file_path):
            logger.warning(f"File not found for paper: {paper_id}")
            raise NotFoundError("PaperFile", paper_id)
        
        return {
            "file_path": paper.file_path,
            "file_size": paper.file_size,
            "upload_date": paper.upload_date,
        }

    async def list_papers_by_conference(self, conference_id: str, skip: int = 0, limit: int = 100) -> list[dict]:
        """
        List papers for a conference.
        
        Args:
            conference_id: Conference ID
            skip: Skip count for pagination
            limit: Limit for pagination
            
        Returns:
            List of papers
        """
        logger.info(f"Listing papers for conference: {conference_id}, skip={skip}, limit={limit}")
        
        papers = self.db.query(PaperModel).filter(
            PaperModel.conference_id == conference_id
        ).offset(skip).limit(limit).all()
        
        result = []
        for paper in papers:
            result.append({
                "id": paper.id,
                "title": paper.title,
                "authors": paper.authors,
                "status": paper.status,
                "upload_date": paper.upload_date,
            })
        
        return result
