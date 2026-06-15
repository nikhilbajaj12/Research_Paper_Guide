"""Paper upload routes."""

import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Form, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..core import get_logger, settings
from ..schemas import PaperUploadResponse
from ..utils.file_utils import (
    validate_file_extension, validate_file_size,
    get_file_extension, safe_filename, ensure_upload_directory, get_file_size
)
from ..services.parser_service import ParserService
from ..cache.parsed_document_cache import ParsedDocumentCache
from .compliance import PAPER_STORAGE

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/papers", tags=["papers"])

parser_service = ParserService()
parsed_doc_cache = ParsedDocumentCache()


@router.post("/upload", response_model=PaperUploadResponse)
async def upload_paper(
    file: UploadFile = File(...),
    conference_id: str = Form(...),
    db: Session = Depends(get_db),
):
    """Upload a research paper file."""
    logger.info(f"Uploading file: {file.filename} for conference: {conference_id}")

    if not validate_file_extension(file.filename):
        logger.warning(f"Invalid file type: {file.filename}")
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Allowed: PDF, DOCX, ZIP"
        )

    try:
        contents = await file.read()
        file_size = len(contents)

        if not validate_file_size(file_size):
            logger.warning(f"File too large: {file.filename}")
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {settings.MAX_PDF_SIZE_MB}MB"
            )

        ensure_upload_directory()
        paper_id = str(uuid.uuid4())
        ext = get_file_extension(file.filename)
        storage_filename = f"{paper_id}.{ext}"
        storage_path = os.path.join(settings.LOCAL_STORAGE_PATH, storage_filename)

        with open(storage_path, 'wb') as f:
            f.write(contents)

        PAPER_STORAGE[paper_id] = {
            "file_name": file.filename,
            "file_type": ext,
            "storage_path": storage_path,
            "conference_id": conference_id,
        }

        # Parse once immediately and cache the result (memory + db)
        parsed = parser_service.parse(storage_path, ext, paper_id)
        await parsed_doc_cache.set(paper_id, parsed, db)
        logger.info(f"Cache store: paper={paper_id} (parsed once during upload)")

        return PaperUploadResponse(
            paper_id=paper_id,
            file_name=file.filename,
            file_type=ext,
            file_size=file_size,
            storage_path=storage_path,
            upload_status="completed"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to upload file"
        )
