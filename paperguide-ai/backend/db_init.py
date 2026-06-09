"""Database initialization and seed script."""

import os
import sys
from sqlalchemy.orm import Session

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal, init_db
from app.utils.data_loader import load_initial_data
from app.core import get_logger

logger = get_logger(__name__)


def init_database():
    """Initialize database schema."""
    logger.info("Initializing database schema...")
    init_db()
    logger.info("Database schema initialized")


def seed_database():
    """Load initial data into database."""
    logger.info("Seeding database with initial data...")
    db = SessionLocal()
    try:
        stats = load_initial_data(db)
        logger.info(f"Database seeding complete: {stats}")
        print(f"\n✓ Database seeding complete:")
        for key, value in stats.items():
            print(f"  - {key}: {value} items")
    except Exception as e:
        logger.error(f"Error seeding database: {str(e)}")
        print(f"✗ Error seeding database: {str(e)}")
    finally:
        db.close()


def reset_database():
    """Reset database (drop all tables and recreate)."""
    logger.warning("Resetting database...")
    from app.database import Base, engine
    
    logger.warning("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    logger.warning("All tables dropped")
    
    init_database()
    seed_database()
    logger.info("Database reset complete")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database management utilities")
    parser.add_argument(
        "action",
        choices=["init", "seed", "reset"],
        help="Action to perform"
    )
    
    args = parser.parse_args()
    
    if args.action == "init":
        init_database()
        print("✓ Database initialized")
    elif args.action == "seed":
        seed_database()
    elif args.action == "reset":
        reset_database()
        print("✓ Database reset complete")
