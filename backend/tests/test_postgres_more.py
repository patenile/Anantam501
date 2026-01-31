import os
import pytest
import psycopg2
from sqlalchemy import create_engine, text
import datetime

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
PARTITIONED_TABLE = "partitioned_table"
TRIGGER_TABLE = "trigger_table"
VIEW_NAME = "test_view"
MVIEW_NAME = "test_mview"
FTS_TABLE = "fts_table"
LOB_TABLE = "lob_table"


@pytest.fixture(scope="module")
def setup_partitioned_table():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(
            text(f"DROP TABLE IF EXISTS {SCHEMA_NAME}.{PARTITIONED_TABLE} CASCADE;")
        )
        conn.execute(
            text(
                f"CREATE TABLE {SCHEMA_NAME}.{PARTITIONED_TABLE} "
                f"(id INT, created_at DATE) PARTITION BY RANGE (created_at);"
            )
        )
        conn.execute(
            text(
                f"CREATE TABLE {SCHEMA_NAME}.{PARTITIONED_TABLE}_2024 PARTITION OF "
                f"{SCHEMA_NAME}.{PARTITIONED_TABLE} "
                "FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');"
            )
        )
    yield
    with engine.connect() as conn:
        conn.execute(
            text(f"DROP TABLE IF EXISTS {SCHEMA_NAME}.{PARTITIONED_TABLE} CASCADE;")
        )


def test_partitioned_table_insert_and_select(setup_partitioned_table):
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(
            text(
                f"INSERT INTO {SCHEMA_NAME}.{PARTITIONED_TABLE} "
                f"(id, created_at) VALUES (1, '2024-06-01');"
            )
        )
        result = conn.execute(
            text(f"SELECT id FROM {SCHEMA_NAME}.{PARTITIONED_TABLE}_2024 WHERE id = 1;")
        )
        assert result.fetchone()[0] == 1


@pytest.fixture(scope="module")
def setup_trigger_table():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(
            text(f"DROP TABLE IF EXISTS {SCHEMA_NAME}.{TRIGGER_TABLE} CASCADE;")
        )
        conn.execute(
            text(
                f"CREATE TABLE {SCHEMA_NAME}.{TRIGGER_TABLE} "
                f"(id SERIAL PRIMARY KEY, val INT, updated_at TIMESTAMP);"
            )
        )
        conn.execute(
            text(
                "CREATE OR REPLACE FUNCTION update_timestamp() "
                "RETURNS TRIGGER AS $$ BEGIN NEW.updated_at = NOW(); \
                    RETURN NEW; END; $$ LANGUAGE plpgsql;"
            )
        )
        conn.execute(
            text(
                f"CREATE TRIGGER set_timestamp BEFORE UPDATE ON "
                f"{SCHEMA_NAME}.{TRIGGER_TABLE} "
                "FOR EACH ROW EXECUTE FUNCTION "
                "update_timestamp();"
            )
        )
    yield
    with engine.connect() as conn:
        conn.execute(
            text(f"DROP TABLE IF EXISTS {SCHEMA_NAME}.{TRIGGER_TABLE} CASCADE;")
        )
        conn.execute(text("DROP FUNCTION IF EXISTS update_timestamp();"))


def test_trigger_functionality(setup_trigger_table):
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(
            text(f"INSERT INTO {SCHEMA_NAME}.{TRIGGER_TABLE} (val) VALUES (10);")
        )
        conn.execute(
            text(f"UPDATE {SCHEMA_NAME}.{TRIGGER_TABLE} SET val = 20 WHERE val = 10;")
        )
        result = conn.execute(
            text(
                f"SELECT updated_at FROM {SCHEMA_NAME}.{TRIGGER_TABLE} WHERE val = 20;"
            )
        )
        assert result.fetchone()[0] is not None


@pytest.fixture(scope="module")
def setup_views():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(text(f"DROP VIEW IF EXISTS {SCHEMA_NAME}.{VIEW_NAME};"))
        conn.execute(
            text(
                f"CREATE VIEW {SCHEMA_NAME}.{VIEW_NAME} \
            AS SELECT 1 AS val;"
            )
        )
        conn.execute(
            text(f"DROP MATERIALIZED VIEW IF EXISTS {SCHEMA_NAME}.{MVIEW_NAME};")
        )
        conn.execute(
            text(
                f"CREATE MATERIALIZED VIEW {SCHEMA_NAME}.{MVIEW_NAME} \
                    AS SELECT NOW() AS ts;"
            )
        )
    yield
    with engine.connect() as conn:
        conn.execute(text(f"DROP VIEW IF EXISTS {SCHEMA_NAME}.{VIEW_NAME};"))
        conn.execute(
            text(f"DROP MATERIALIZED VIEW IF EXISTS {SCHEMA_NAME}.{MVIEW_NAME};")
        )


def test_views_and_materialized_views(setup_views):
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(
            text(
                f"SELECT val FROM \
            {SCHEMA_NAME}.{VIEW_NAME};"
            )
        )
        assert result.fetchone()[0] == 1
        result = conn.execute(
            text(
                f"SELECT ts FROM \
            {SCHEMA_NAME}.{MVIEW_NAME};"
            )
        )
        assert result.fetchone()[0] is not None


def test_full_text_search():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(text(f"DROP TABLE IF EXISTS {SCHEMA_NAME}.{FTS_TABLE};"))
        conn.execute(
            text(
                f"CREATE TABLE {SCHEMA_NAME}.{FTS_TABLE} \
                    (id SERIAL PRIMARY KEY, content TEXT);"
            )
        )
        conn.execute(
            text(
                f"INSERT INTO {SCHEMA_NAME}.{FTS_TABLE} (content) \
                    VALUES ('hello world'), ('goodbye world');"
            )
        )
        result = conn.execute(
            text(
                f"SELECT id FROM {SCHEMA_NAME}.{FTS_TABLE} WHERE \
                    to_tsvector('english', content) \
                        @@ plainto_tsquery('english', 'hello');"
            )
        )
        assert result.fetchone()[0] == 1
        conn.execute(text(f"DROP TABLE IF EXISTS {SCHEMA_NAME}.{FTS_TABLE};"))


def test_time_zone_handling():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(text(f"DROP TABLE IF EXISTS {SCHEMA_NAME}.tz_table;"))
        conn.execute(
            text(
                f"CREATE TABLE {SCHEMA_NAME}.tz_table (id SERIAL PRIMARY KEY,\
                    ts TIMESTAMPTZ);"
            )
        )
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        conn.execute(
            text(f"INSERT INTO {SCHEMA_NAME}.tz_table (ts) VALUES (:ts);"),
            {"ts": now_utc},
        )
        result = conn.execute(
            text(f"SELECT ts FROM {SCHEMA_NAME}.tz_table;")
        ).fetchone()[0]
        assert result.tzinfo is not None
        conn.execute(text(f"DROP TABLE IF EXISTS {SCHEMA_NAME}.tz_table;"))


def test_large_object_usage():
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
    )
    cur = conn.cursor()
    cur.execute(f"DROP TABLE IF EXISTS {SCHEMA_NAME}.{LOB_TABLE};")
    cur.execute(
        f"CREATE TABLE {SCHEMA_NAME}.{LOB_TABLE} (id SERIAL PRIMARY KEY, data OID);"
    )
    lobj = conn.lobject(0, "w")
    lobj.write(b"hello large object")
    cur.execute(
        f"INSERT INTO {SCHEMA_NAME}.{LOB_TABLE} (data) VALUES (%s) RETURNING id;",
        (lobj.oid,),
    )
    row_id = cur.fetchone()[0]
    cur.execute(f"SELECT data FROM {SCHEMA_NAME}.{LOB_TABLE} WHERE id = %s;", (row_id,))
    oid = cur.fetchone()[0]
    lobj2 = conn.lobject(oid, "r")
    assert lobj2.read() == b"hello large object"
    lobj2.close()
    lobj.close()
    cur.execute(f"DROP TABLE IF EXISTS {SCHEMA_NAME}.{LOB_TABLE};")
    conn.commit()
    cur.close()
    conn.close()


def test_extension_usage():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS hstore;"))
        result = conn.execute(
            text("SELECT extname FROM pg_extension WHERE extname = 'hstore';")
        )
        assert result.fetchone()[0] == "hstore"
        conn.execute(text("DROP EXTENSION IF EXISTS hstore;"))
