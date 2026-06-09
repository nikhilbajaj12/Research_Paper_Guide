"""Unit tests for checkers."""

import pytest
# TODO: Import checkers
# from app.checkers import PageLimitChecker


@pytest.mark.asyncio
async def test_page_limit_checker_exceeds_limit(sample_paper, neurips_guidelines):
    """
    Test that PageLimitChecker detects page limit violations.
    
    TODO: Implement test
    """
    # TODO: Create checker
    # TODO: Run check
    # TODO: Assert issue detected
    pass


@pytest.mark.asyncio
async def test_page_limit_checker_within_limit(sample_paper, neurips_guidelines):
    """
    Test that PageLimitChecker passes when within limit.
    
    TODO: Implement test
    """
    pass
