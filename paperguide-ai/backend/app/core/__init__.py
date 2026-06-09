"""Core module: configuration, logging, constants, and exceptions."""

from .config import Settings, settings
from .logger import get_logger
from .exceptions import (
    PaperGuideException,
    FileProcessingError,
    ComplianceError,
    NotFoundError,
    ValidationError,
)

__all__ = [
    "Settings",
    "settings",
    "get_logger",
    "PaperGuideException",
    "FileProcessingError",
    "ComplianceError",
    "NotFoundError",
    "ValidationError",
]
