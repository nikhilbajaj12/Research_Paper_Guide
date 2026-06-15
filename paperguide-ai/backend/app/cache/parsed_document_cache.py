"""ParsedDocument cache - parse once, reuse everywhere."""

import json
from typing import Optional, Dict
from sqlalchemy.orm import Session
from ..models.paper_analysis import PaperAnalysis
from ..schemas import ParsedDocument
from ..core import get_logger

logger = get_logger(__name__)


class ParsedDocumentCache:
    """Cache for parsed documents, backed by SQLite for persistence.

    Usage:
        cache = ParsedDocumentCache()
        await cache.set(paper_id, parsed_doc, db)
        doc = await cache.get(paper_id, db)
    """

    _memory_cache: Dict[str, ParsedDocument] = {}

    async def get(self, paper_id: str, db: Optional[Session] = None) -> Optional[ParsedDocument]:
        """Retrieve parsed document by paper_id."""
        if paper_id in self._memory_cache:
            logger.debug(f"Cache HIT (memory) for paper: {paper_id}")
            return self._memory_cache[paper_id]

        if db is not None:
            record = db.query(PaperAnalysis).filter(
                PaperAnalysis.paper_id == paper_id
            ).first()

            if record:
                logger.debug(f"Cache HIT (db) for paper: {paper_id}")
                try:
                    data = json.loads(record.parsed_document_json)
                    doc = ParsedDocument.from_dict(data)
                    self._memory_cache[paper_id] = doc
                    return doc
                except (json.JSONDecodeError, KeyError) as e:
                    logger.error(f"Cache read error for {paper_id}: {e}")
                    return None

        logger.debug(f"Cache MISS for paper: {paper_id}")
        return None

    async def set(self, paper_id: str, doc: ParsedDocument, db: Optional[Session] = None) -> None:
        """Store parsed document."""
        self._memory_cache[paper_id] = doc

        if db is None:
            logger.debug(f"Parsed document cached in memory for paper: {paper_id}")
            return

        try:
            doc_json = json.dumps(doc.to_dict(), default=str)
            existing = db.query(PaperAnalysis).filter(
                PaperAnalysis.paper_id == paper_id
            ).first()

            if existing:
                existing.parsed_document_json = doc_json
            else:
                record = PaperAnalysis(
                    paper_id=paper_id,
                    parsed_document_json=doc_json,
                )
                db.add(record)

            db.commit()
            logger.info(f"Parsed document cached (memory+db) for paper: {paper_id}")
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to cache parsed document for {paper_id}: {e}")

    async def delete(self, paper_id: str, db: Optional[Session] = None) -> None:
        """Remove cached parsed document."""
        self._memory_cache.pop(paper_id, None)

        if db is not None:
            db.query(PaperAnalysis).filter(
                PaperAnalysis.paper_id == paper_id
            ).delete()
            db.commit()
            logger.info(f"Parsed document evicted from db for paper: {paper_id}")


# Singleton instance
parsed_document_cache = ParsedDocumentCache()
