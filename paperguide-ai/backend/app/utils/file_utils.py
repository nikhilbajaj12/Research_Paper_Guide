"""File utilities."""

import os
import re
from pathlib import Path
from ..core import get_logger, settings

logger = get_logger(__name__)


def validate_file_extension(filename: str) -> bool:
    """Validate file extension against allowed formats."""
    if not filename:
        return False
    ext = os.path.splitext(filename)[1].lower()
    return ext in settings.ACCEPTED_FILE_FORMATS


def validate_file_size(file_size_bytes: int) -> bool:
    """Validate file size against max allowed."""
    max_size_bytes = settings.MAX_PDF_SIZE_MB * 1024 * 1024
    return file_size_bytes <= max_size_bytes


def get_file_extension(filename: str) -> str:
    """Get file extension from filename."""
    if not filename:
        return ""
    _, ext = os.path.splitext(filename)
    return ext.lower()


def safe_filename(filename: str) -> str:
    """Convert filename to safe format by removing special characters."""
    if not filename:
        return "unnamed_file"
    safe_name = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    return safe_name[:255]


def ensure_upload_directory() -> str:
    """Create upload directory if it doesn't exist, return path."""
    upload_dir = settings.LOCAL_STORAGE_PATH
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir, exist_ok=True)
        logger.info(f"Created upload directory: {upload_dir}")
    return upload_dir


def get_file_size(file_path: str) -> int:
    """Get file size in bytes."""
    if not os.path.exists(file_path):
        return 0
    return os.path.getsize(file_path)


async def save_upload_file(file_content: bytes, filename: str, subdirectory: str = "papers") -> str:
    """Save uploaded file to storage."""
    logger.info(f"Saving file: {filename} to {subdirectory}")
    # TODO: Implement file saving
    return ""


async def delete_file(file_path: str) -> bool:
    """Delete a file."""
    logger.info(f"Deleting file: {file_path}")
    # TODO: Implement file deletion
    return False


def ensure_directory_exists(directory: str) -> bool:
    """
    Ensure directory exists, create if not.
    
    TODO: Implement directory creation
    """
    logger.debug(f"Ensuring directory exists: {directory}")
    # TODO: Check if directory exists
    # TODO: Create if needed
    # TODO: Return success status
    return True
