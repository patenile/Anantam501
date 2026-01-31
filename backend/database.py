import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# Use TEST_DATABASE_URL if running under pytest, else use DATABASE_URL

if any("pytest" in arg for arg in sys.argv) or os.getenv("PYTEST_CURRENT_TEST"):
    db_url = os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL")
else:
    db_url = os.getenv("DATABASE_URL")

engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Add Base for Alembic
Base = declarative_base()


def get_test_database_url():
    # Always return the test DB URL for seeding
    return os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL")
