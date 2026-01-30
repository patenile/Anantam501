import os
import pytest
import psycopg2
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String

DB_NAME = os.getenv("TEST_DB", "anantam_test")
DB_USER = os.getenv("TEST_DB_USER", "anantam")
DB_PASSWORD = os.getenv("TEST_DB_PASSWORD", "supersecret")
DB_HOST = os.getenv("TEST_DB_HOST", "db")
DB_PORT = os.getenv("TEST_DB_PORT", "5432")
DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
)

SCHEMA_NAME = "test_schema"
TABLE_NAME = "test_table"


@pytest.fixture(scope="module")
def clean_schema():
    # Drop schema if exists, then create it fresh
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
    )
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(f"DROP SCHEMA IF EXISTS {SCHEMA_NAME} CASCADE;")
    cur.execute(f"CREATE SCHEMA {SCHEMA_NAME};")
    cur.close()
    conn.close()
    yield
    # Cleanup after tests
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
    )
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(f"DROP SCHEMA IF EXISTS {SCHEMA_NAME} CASCADE;")
    cur.close()
    conn.close()


def test_create_table_raw_sql(clean_schema):
    """Test creating a table in a specific schema using raw SQL."""
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
    )
    cur = conn.cursor()
    cur.execute(f"""
        CREATE TABLE {SCHEMA_NAME}.{TABLE_NAME} (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL
        );
    """)
    cur.execute(
        f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{SCHEMA_NAME}' AND table_name = '{TABLE_NAME}';"
    )
    assert cur.fetchone()[0] == TABLE_NAME
    cur.close()
    conn.close()


def test_create_table_sqlalchemy(clean_schema):
    """Test creating a table in a specific schema using SQLAlchemy."""
    engine = create_engine(DATABASE_URL)
    metadata = MetaData(schema=SCHEMA_NAME)
    test_table = Table(
        TABLE_NAME,
        metadata,
        Column("id", Integer, primary_key=True),
        Column("name", String(100), nullable=False),
    )
    metadata.create_all(engine)
    insp = engine.dialect.get_inspector(engine)
    tables = insp.get_table_names(schema=SCHEMA_NAME)
    assert TABLE_NAME in tables
    # Cleanup
    metadata.drop_all(engine)
