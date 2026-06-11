"""Package generation and download routes."""

import os
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import PackageGenerationRequest, PackageGenerationResponse
from ..services.package_service import PackageService, PACKAGE_STORAGE
from ..routes.compliance import (
    PAPER_STORAGE as COMPLIANCE_PAPER_STORAGE,
    COMPLIANCE_REPORT_STORAGE,
)
from ..services.parser_service import ParserService
from ..core import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/packages", tags=["packages"])

package_service = PackageService()


@router.post("/generate", response_model=PackageGenerationResponse)
async def generate_package(
    request: PackageGenerationRequest,
    db: Session = Depends(get_db)
):
    """Generate Overleaf-ready LaTeX package."""
    logger.info(f"Generating package for paper: {request.paper_id}")
    
    try:
        paper_id = request.paper_id
        
        if paper_id not in COMPLIANCE_PAPER_STORAGE:
            raise HTTPException(
                status_code=404,
                detail=f"Paper not found: {paper_id}"
            )
        
        paper_info = COMPLIANCE_PAPER_STORAGE[paper_id]
        storage_path = paper_info["storage_path"]
        file_type = paper_info["file_type"]
        
        if not os.path.exists(storage_path):
            raise HTTPException(
                status_code=404,
                detail="Paper file not found"
            )
        
        parser_service = ParserService()
        parsed_paper = parser_service.parse(storage_path, file_type)
        
        compliance_report = COMPLIANCE_REPORT_STORAGE.get(paper_id)
        if not compliance_report:
            raise HTTPException(
                status_code=409,
                detail="Run compliance analysis before generating a package"
            )
        if compliance_report.get("conference_id") != request.conference_id:
            raise HTTPException(
                status_code=409,
                detail="Run compliance analysis for the selected conference before generating a package"
            )
        
        package_id, package_metadata = package_service.generate_package(
            paper_id=paper_id,
            conference_id=request.conference_id,
            parsed_paper=parsed_paper,
            compliance_report=compliance_report,
            project_id=request.project_id,
            package_type=request.package_type
        )
        
        return PackageGenerationResponse(
            package_id=package_id,
            project_id=request.project_id,
            paper_id=paper_id,
            conference_id=request.conference_id,
            package_type=request.package_type,
            zip_file_path=package_metadata.get('zip_file_path'),
            generated_files=package_metadata.get('generated_files', []),
            status=package_metadata.get('status'),
            message=package_metadata.get('message'),
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating package: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate package: {str(e)}"
        )


@router.get("/{package_id}/download")
async def download_package(package_id: str):
    """Download generated package ZIP."""
    logger.info(f"Downloading package: {package_id}")
    
    try:
        package = PACKAGE_STORAGE.get(package_id)
        
        if not package:
            raise HTTPException(
                status_code=404,
                detail=f"Package not found: {package_id}"
            )
        
        zip_path = package.get('zip_file_path')
        
        if not zip_path or not os.path.exists(zip_path):
            raise HTTPException(
                status_code=404,
                detail="Package file not found on server"
            )
        
        return FileResponse(
            path=zip_path,
            filename=os.path.basename(zip_path),
            media_type='application/zip'
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading package: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to download package"
        )
