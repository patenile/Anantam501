import os
import pytest
import psycopg2
from sqlalchemy import create_engine, text

# Use test DB environment variables
DB_NAME = os.getenv("TEST_DB", "anantam_test")
DB_USER = os.getenv("TEST_DB_USER", "anantam")
DB_PASSWORD = os.getenv("TEST_DB_PASSWORD", "supersecret")
DB_HOST = os.getenv("TEST_DB_HOST", "db")
DB_PORT = os.getenv("TEST_DB_PORT", "5432")
DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
)


def test_psycopg2_connection():
    """Test direct connection to PostgreSQL using psycopg2."""
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
    )
    cur = conn.cursor()
    cur.execute("SELECT 1")
    assert cur.fetchone()[0] == 1
    cur.close()
    conn.close()


def test_sqlalchemy_connection():
    """Test connection to PostgreSQL using SQLAlchemy."""
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar() == 1


def test_authentication_failure():
    """Test authentication failure with wrong password."""
    with pytest.raises(Exception):
        psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password="wrongpassword",
            host=DB_HOST,
            port=DB_PORT,
        )
