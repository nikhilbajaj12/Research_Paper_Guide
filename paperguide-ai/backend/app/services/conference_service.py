"""Conference service."""

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from datetime import datetime, timedelta
from ..models import Conference as ConferenceModel, ConferenceGuidelines as GuidelinesModel
from ..schemas import ConferenceBrief, ConferenceDetailed, ConferenceGuidelines
from ..core import get_logger, NotFoundError

logger = get_logger(__name__)


class ConferenceService:
    """Service for conference operations."""

    def __init__(self, db: Session):
        """Initialize service."""
        self.db = db

    async def get_all_conferences(self, skip: int = 0, limit: int = 100) -> list[ConferenceBrief]:
        """
        Get all conferences with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of ConferenceBrief objects
        """
        logger.info(f"Retrieving conferences: skip={skip}, limit={limit}")
        
        conferences = self.db.query(ConferenceModel).offset(skip).limit(limit).all()
        
        result = []
        for conf in conferences:
            result.append(ConferenceBrief(
                id=conf.id,
                abbr=conf.abbr,
                name=conf.name,
                start_date=conf.start_date,
                submission_deadline=conf.submission_deadline,
                location=conf.location,
                flag=conf.flag,
                conference_type=conf.conference_type,
                topics=conf.topics,
                description=conf.description,
            ))
        
        return result

    async def get_conference_by_id(self, conference_id: str) -> ConferenceDetailed:
        """
        Get conference details by ID with guidelines.
        
        Args:
            conference_id: Conference ID
            
        Returns:
            ConferenceDetailed with guidelines
            
        Raises:
            NotFoundError: If conference not found
        """
        logger.info(f"Retrieving conference: {conference_id}")
        
        conference = self.db.query(ConferenceModel).filter(
            ConferenceModel.id == conference_id
        ).first()
        
        if not conference:
            logger.warning(f"Conference not found: {conference_id}")
            raise NotFoundError("Conference", conference_id)
        
        guidelines = self.db.query(GuidelinesModel).filter(
            GuidelinesModel.conference_id == conference_id
        ).first()
        
        guidelines_obj = None
        if guidelines:
            guidelines_obj = ConferenceGuidelines(
                conference_id=guidelines.conference_id,
                max_pages=guidelines.max_pages,
                min_pages=guidelines.min_pages,
                requires_anonymity=guidelines.requires_anonymity,
                reference_format=guidelines.reference_format,
                margin_top_cm=guidelines.margin_top_cm,
                margin_bottom_cm=guidelines.margin_bottom_cm,
                margin_left_cm=guidelines.margin_left_cm,
                margin_right_cm=guidelines.margin_right_cm,
                required_sections=guidelines.required_sections,
                forbidden_topics=guidelines.forbidden_topics,
                special_rules=guidelines.special_rules,
                notes=guidelines.notes,
            )
        
        return ConferenceDetailed(
            id=conference.id,
            abbr=conference.abbr,
            name=conference.name,
            start_date=conference.start_date,
            submission_deadline=conference.submission_deadline,
            location=conference.location,
            flag=conference.flag,
            conference_type=conference.conference_type,
            topics=conference.topics,
            description=conference.description,
            url=conference.url,
            guidelines=guidelines_obj,
            notification_date=conference.notification_date,
            acceptance_rate=conference.acceptance_rate,
        )

    async def filter_conferences(
        self,
        search: str = None,
        conference_types: list[str] = None,
        topics: list[str] = None,
        deadline_within_days: int = None,
    ) -> list[ConferenceBrief]:
        """
        Filter conferences with multiple criteria.
        
        Args:
            search: Search text in name, location, topics
            conference_types: Filter by conference type
            topics: Filter by topics
            deadline_within_days: Show only conferences with deadline within N days
            
        Returns:
            Filtered list of ConferenceBrief objects
        """
        logger.info(f"Filtering conferences: search={search}, types={conference_types}, deadline_within={deadline_within_days}")
        
        query = self.db.query(ConferenceModel)
        
        # Search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    ConferenceModel.name.ilike(search_term),
                    ConferenceModel.location.ilike(search_term),
                    ConferenceModel.abbr.ilike(search_term),
                )
            )
        
        # Conference type filter
        if conference_types:
            query = query.filter(ConferenceModel.conference_type.in_(conference_types))
        
        # Deadline filter
        if deadline_within_days:
            today = datetime.utcnow().date()
            deadline = today + timedelta(days=deadline_within_days)
            query = query.filter(
                and_(
                    ConferenceModel.submission_deadline >= str(today),
                    ConferenceModel.submission_deadline <= str(deadline),
                )
            )
        
        conferences = query.all()
        
        result = []
        for conf in conferences:
            result.append(ConferenceBrief(
                id=conf.id,
                abbr=conf.abbr,
                name=conf.name,
                start_date=conf.start_date,
                submission_deadline=conf.submission_deadline,
                location=conf.location,
                flag=conf.flag,
                conference_type=conf.conference_type,
                topics=conf.topics,
                description=conf.description,
            ))
        
        return result

    async def get_guidelines(self, conference_id: str) -> ConferenceGuidelines:
        """
        Get guidelines for a conference.
        
        Args:
            conference_id: Conference ID
            
        Returns:
            ConferenceGuidelines object
            
        Raises:
            NotFoundError: If guidelines not found
        """
        logger.info(f"Getting guidelines for: {conference_id}")
        
        guidelines = self.db.query(GuidelinesModel).filter(
            GuidelinesModel.conference_id == conference_id
        ).first()
        
        if not guidelines:
            logger.warning(f"Guidelines not found for: {conference_id}")
            raise NotFoundError("ConferenceGuidelines", conference_id)
        
        return ConferenceGuidelines(
            conference_id=guidelines.conference_id,
            max_pages=guidelines.max_pages,
            min_pages=guidelines.min_pages,
            requires_anonymity=guidelines.requires_anonymity,
            reference_format=guidelines.reference_format,
            margin_top_cm=guidelines.margin_top_cm,
            margin_bottom_cm=guidelines.margin_bottom_cm,
            margin_left_cm=guidelines.margin_left_cm,
            margin_right_cm=guidelines.margin_right_cm,
            required_sections=guidelines.required_sections,
            forbidden_topics=guidelines.forbidden_topics,
            special_rules=guidelines.special_rules,
            notes=guidelines.notes,
        )
