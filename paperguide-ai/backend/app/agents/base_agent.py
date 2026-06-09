"""Base agent class."""

from abc import ABC, abstractmethod
from ..core import get_logger

logger = get_logger(__name__)


class BaseAgent(ABC):
    """Abstract base class for all agents."""

    def __init__(self):
        """Initialize agent."""
        self.name = self.__class__.__name__

    @abstractmethod
    async def process(self, **kwargs) -> dict:
        """
        Process data with agent logic (typically LLM-powered).
        
        TODO: Implement in Phase 2
        
        Returns:
            Dictionary with results
        """
        pass
