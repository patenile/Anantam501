"""
test_seed.py: Test data seeding for integration/E2E tests.

- Seeds the test database with known users and data for integration/E2E tests
- Should be run after DB migrations and before tests
- Uses the same models and DB config as the backend
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User
from database import get_test_database_url
import hashlib


def hash_password(password):
    # Simple hash for test data (not for production)
    return hashlib.sha256(password.encode()).hexdigest()


def seed():
    db_url = get_test_database_url()
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    # Clear users table
    session.query(User).delete()
    # Add test users
    users = [
        User(
            email="testuser1@example.com",
            hashed_password=hash_password("password1"),
            full_name="Test User 1",
            is_superuser=False,
        ),
        User(
            email="admin@example.com",
            hashed_password=hash_password("adminpass"),
            full_name="Admin User",
            is_superuser=True,
        ),
    ]
    session.add_all(users)
    session.commit()
    print("[INFO] Seeded test users.")
    session.close()


if __name__ == "__main__":
    seed()
