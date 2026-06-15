"""PaperAnalysis ORM model for persistent parsed document cache."""

from sqlalchemy import Column, String, DateTime, Text
from datetime import datetime
from . import Base


class PaperAnalysis(Base):
    """Persistent storage for parsed document data."""

    __tablename__ = "paper_analyses"

    paper_id = Column(String, primary_key=True)
    parsed_document_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<PaperAnalysis {self.paper_id}>"
