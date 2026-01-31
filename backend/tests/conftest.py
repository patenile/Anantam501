import sys
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from database import Base
from main import app

# Ensure backend/ is on sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# --- Test Database Setup ---

# Use DATABASE_URL from env or fallback to a default test DB
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///test.db")

# --- Test Database Setup ---


@pytest.fixture(scope="session")
def test_db_engine():
    # Use a separate test DB (ensure DATABASE_URL points to a test DB!)
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(test_db_engine):
    connection = test_db_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session, monkeypatch):
    # Patch get_db to use the test session
    def override_get_db():
        yield db_session

    app.dependency_overrides = {}
    app.dependency_overrides["get_db"] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides = {}
