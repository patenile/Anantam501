import os
import pytest
import psycopg2
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String
from sqlalchemy.orm import Session

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
def setup_table():
    # Ensure schema and table exist, clean before/after
    engine = create_engine(DATABASE_URL)
    metadata = MetaData(schema=SCHEMA_NAME)
    test_table = Table(
        TABLE_NAME,
        metadata,
        Column("id", Integer, primary_key=True),
        Column("name", String(100), nullable=False),
    )
    metadata.drop_all(engine)
    metadata.create_all(engine)
    yield test_table
    metadata.drop_all(engine)


def test_crud_raw_sql(setup_table):
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
    )
    cur = conn.cursor()
    # Insert
    cur.execute(
        f"INSERT INTO {SCHEMA_NAME}.{TABLE_NAME} (name) VALUES ('Alice') RETURNING id;"
    )
    row_id = cur.fetchone()[0]
    # Select
    cur.execute(
        f"SELECT name FROM {SCHEMA_NAME}.{TABLE_NAME} WHERE id = %s;", (row_id,)
    )
    assert cur.fetchone()[0] == "Alice"
    # Update
    cur.execute(
        f"UPDATE {SCHEMA_NAME}.{TABLE_NAME} SET name = 'Bob' WHERE id = %s;", (row_id,)
    )
    cur.execute(
        f"SELECT name FROM {SCHEMA_NAME}.{TABLE_NAME} WHERE id = %s;", (row_id,)
    )
    assert cur.fetchone()[0] == "Bob"
    # Delete
    cur.execute(f"DELETE FROM {SCHEMA_NAME}.{TABLE_NAME} WHERE id = %s;", (row_id,))
    cur.execute(
        f"SELECT COUNT(*) FROM {SCHEMA_NAME}.{TABLE_NAME} WHERE id = %s;", (row_id,)
    )
    assert cur.fetchone()[0] == 0
    conn.commit()
    cur.close()
    conn.close()


def test_crud_sqlalchemy(setup_table):
    engine = create_engine(DATABASE_URL)
    test_table = setup_table
    with Session(engine) as session:
        # Insert
        ins = test_table.insert().values(name="Charlie")
        result = session.execute(ins)
        row_id = result.inserted_primary_key[0]
        session.commit()
        # Select
        sel = test_table.select().where(test_table.c.id == row_id)
        row = session.execute(sel).fetchone()
        assert row["name"] == "Charlie"
        # Update
        upd = test_table.update().where(test_table.c.id == row_id).values(name="Dana")
        session.execute(upd)
        session.commit()
        row = session.execute(sel).fetchone()
        assert row["name"] == "Dana"
        # Delete
        dele = test_table.delete().where(test_table.c.id == row_id)
        session.execute(dele)
        session.commit()
        row = session.execute(sel).fetchone()
        assert row is None


def test_transaction_rollback(setup_table):
    engine = create_engine(DATABASE_URL)
    test_table = setup_table
    with Session(engine) as session:
        ins = test_table.insert().values(name="Eve")
        result = session.execute(ins)
        row_id = result.inserted_primary_key[0]
        session.rollback()  # Rollback the insert
        sel = test_table.select().where(test_table.c.id == row_id)
        row = session.execute(sel).fetchone()
        assert row is None


def test_unique_constraint(setup_table):
    # Add a unique constraint to name column for this test
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(
            text(
                f"ALTER TABLE {SCHEMA_NAME}.{TABLE_NAME} ADD CONSTRAINT unique_name UNIQUE (name);"
            )
        )
        # Insert a row
        conn.execute(
            text(f"INSERT INTO {SCHEMA_NAME}.{TABLE_NAME} (name) VALUES ('Frank');")
        )
        # Try to insert duplicate
        with pytest.raises(Exception):
            conn.execute(
                text(f"INSERT INTO {SCHEMA_NAME}.{TABLE_NAME} (name) VALUES ('Frank');")
            )
        # Cleanup constraint
        conn.execute(
            text(f"ALTER TABLE {SCHEMA_NAME}.{TABLE_NAME} DROP CONSTRAINT unique_name;")
        )


def test_data_types_and_casting(setup_table):
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        # Insert integer as string, should cast
        conn.execute(
            text(f"INSERT INTO {SCHEMA_NAME}.{TABLE_NAME} (name) VALUES (:val);"),
            {"val": str(123)},
        )
        result = conn.execute(
            text(f"SELECT name FROM {SCHEMA_NAME}.{TABLE_NAME} WHERE name = '123';")
        )
        assert result.fetchone()[0] == "123"
        # Cleanup
        conn.execute(
            text(f"DELETE FROM {SCHEMA_NAME}.{TABLE_NAME} WHERE name = '123';")
        )


def test_error_handling(setup_table):
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        # Try to insert null into NOT NULL column
        with pytest.raises(Exception):
            conn.execute(
                text(f"INSERT INTO {SCHEMA_NAME}.{TABLE_NAME} (name) VALUES (NULL);")
            )
