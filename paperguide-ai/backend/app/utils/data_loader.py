"""Data loading utilities for populating initial conference data."""

import json
import os
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from ..models import Conference as ConferenceModel, ConferenceGuidelines as GuidelinesModel
from ..core import get_logger

logger = get_logger(__name__)


def load_conferences_from_json(db: Session, json_file_path: str = None) -> int:
    """
    Load conference data from JSON file.
    
    Args:
        db: Database session
        json_file_path: Path to conferences.json (auto-locate if None)
        
    Returns:
        Number of conferences loaded
    """
    # Auto-locate conferences.json if not provided
    if json_file_path is None:
        # Try to find conferences.json in data folder
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        json_file_path = os.path.join(base_dir, "data", "conferences.json")
    
    if not os.path.exists(json_file_path):
        logger.warning(f"Conferences file not found: {json_file_path}")
        return 0
    
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
        
        conferences = data if isinstance(data, list) else data.get('conferences', [])
        
        loaded = 0
        for conf_data in conferences:
            # Check if conference already exists
            existing = db.query(ConferenceModel).filter(
                ConferenceModel.id == conf_data.get('id')
            ).first()
            
            if existing:
                logger.info(f"Conference already exists: {conf_data.get('id')}")
                continue
            
            # Create conference model
            conference = ConferenceModel(
                id=conf_data.get('id'),
                abbr=conf_data.get('abbr'),
                name=conf_data.get('name'),
                start_date=conf_data.get('start_date'),
                submission_deadline=conf_data.get('submission_deadline'),
                location=conf_data.get('location'),
                flag=conf_data.get('flag'),
                conference_type=conf_data.get('type', 'workshop'),
                topics=conf_data.get('topics', []),
                description=conf_data.get('description'),
                url=conf_data.get('url'),
                notification_date=conf_data.get('notification_date'),
                acceptance_rate=conf_data.get('acceptance_rate'),
            )
            
            db.add(conference)
            loaded += 1
            logger.info(f"Loaded conference: {conf_data.get('id')}")
        
        if loaded > 0:
            db.commit()
            logger.info(f"Committed {loaded} conferences to database")
        
        return loaded
        
    except Exception as e:
        logger.error(f"Error loading conferences: {str(e)}")
        db.rollback()
        return 0


def load_guidelines_from_json(db: Session, json_file_path: str = None) -> int:
    """
    Load conference guidelines from JSON file.
    
    Args:
        db: Database session
        json_file_path: Path to guidelines JSON file
        
    Returns:
        Number of guideline sets loaded
    """
    # Auto-locate guidelines files
    if json_file_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        guidelines_dir = os.path.join(base_dir, "data", "guidelines")
        
        if not os.path.exists(guidelines_dir):
            logger.warning(f"Guidelines directory not found: {guidelines_dir}")
            return 0
        
        # Load all JSON files from guidelines directory
        loaded = 0
        for filename in os.listdir(guidelines_dir):
            if filename.endswith('.json'):
                json_file_path = os.path.join(guidelines_dir, filename)
                loaded += _load_single_guidelines_file(db, json_file_path)
        
        return loaded
    else:
        return _load_single_guidelines_file(db, json_file_path)


def _load_single_guidelines_file(db: Session, json_file_path: str) -> int:
    """Load a single guidelines JSON file."""
    if not os.path.exists(json_file_path):
        logger.warning(f"Guidelines file not found: {json_file_path}")
        return 0
    
    try:
        with open(json_file_path, 'r') as f:
            guidelines_data = json.load(f)
        
        # Handle both single guideline and list of guidelines
        if isinstance(guidelines_data, dict) and 'conference_id' in guidelines_data:
            guidelines_data = [guidelines_data]
        elif isinstance(guidelines_data, dict) and 'guidelines' in guidelines_data:
            guidelines_data = guidelines_data['guidelines']
        elif not isinstance(guidelines_data, list):
            logger.warning(f"Unexpected format in {json_file_path}")
            return 0
        
        loaded = 0
        for guide_data in guidelines_data:
            # Check if guidelines already exist
            existing = db.query(GuidelinesModel).filter(
                GuidelinesModel.conference_id == guide_data.get('conference_id')
            ).first()
            
            if existing:
                logger.info(f"Guidelines already exist for: {guide_data.get('conference_id')}")
                continue
            
            # Create guidelines model
            guidelines = GuidelinesModel(
                id=str(uuid.uuid4()),  # Generate ID
                conference_id=guide_data.get('conference_id'),
                max_pages=guide_data.get('max_pages'),
                min_pages=guide_data.get('min_pages', 1),
                requires_anonymity=guide_data.get('requires_anonymity', False),
                reference_format=guide_data.get('reference_format', 'bibtex'),
                margin_top_cm=guide_data.get('margin_top_cm', 2.54),
                margin_bottom_cm=guide_data.get('margin_bottom_cm', 2.54),
                margin_left_cm=guide_data.get('margin_left_cm', 2.54),
                margin_right_cm=guide_data.get('margin_right_cm', 2.54),
                required_sections=guide_data.get('required_sections', []),
                forbidden_topics=guide_data.get('forbidden_topics', []),
                special_rules=guide_data.get('special_rules', {}),
                notes=guide_data.get('notes', ''),
            )
            
            db.add(guidelines)
            loaded += 1
            logger.info(f"Loaded guidelines for: {guide_data.get('conference_id')}")
        
        if loaded > 0:
            db.commit()
            logger.info(f"Committed {loaded} guideline sets to database")
        
        return loaded
        
    except Exception as e:
        logger.error(f"Error loading guidelines from {json_file_path}: {str(e)}")
        db.rollback()
        return 0


def load_initial_data(db: Session) -> dict:
    """
    Load all initial data into database.
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with loading statistics
    """
    logger.info("Starting initial data load")
    
    stats = {
        'conferences': load_conferences_from_json(db),
        'guidelines': load_guidelines_from_json(db),
    }
    
    logger.info(f"Data load complete: {stats}")
    return stats
