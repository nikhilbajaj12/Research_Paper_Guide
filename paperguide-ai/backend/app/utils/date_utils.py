"""Date utilities."""

from datetime import datetime, date, timedelta
from ..core import get_logger

logger = get_logger(__name__)


def get_days_until_deadline(deadline: str) -> int:
    """
    Calculate days until deadline (ISO date string).
    
    TODO: Implement calculation
    """
    logger.debug(f"Calculating days until: {deadline}")
    # TODO: Parse deadline
    # TODO: Calculate difference
    # TODO: Return days
    return 0


def format_date(date_str: str, format_str: str = "%Y-%m-%d") -> str:
    """
    Format date string.
    
    TODO: Implement formatting
    """
    # TODO: Parse input date
    # TODO: Format to desired format
    # TODO: Return formatted string
    return ""


def is_past_deadline(deadline: str) -> bool:
    """
    Check if deadline has passed.
    
    TODO: Implement check
    """
    # TODO: Calculate days until
    # TODO: Return True if negative
    return False
