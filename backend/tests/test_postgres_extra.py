import os
import pytest
import psycopg2
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, ForeignKey, Index, JSON, ARRAY
from sqlalchemy.orm import Session

DB_NAME = os.getenv("TEST_DB", "anantam_test")
DB_USER = os.getenv("TEST_DB_USER", "anantam")
DB_PASSWORD = os.getenv("TEST_DB_PASSWORD", "supersecret")
DB_HOST = os.getenv("TEST_DB_HOST", "db")
DB_PORT = os.getenv("TEST_DB_PORT", "5432")
DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

SCHEMA_NAME = "test_schema"
PARENT_TABLE = "parent_table"
CHILD_TABLE = "child_table"

@pytest.fixture(scope="module")
def setup_advanced_schema():
    engine = create_engine(DATABASE_URL)
    metadata = MetaData(schema=SCHEMA_NAME)
    parent = Table(
        PARENT_TABLE, metadata,
        Column('id', Integer, primary_key=True),
        Column('info', String(50)),
        Column('data', JSON),
        Column('tags', ARRAY(String)),
        Index('ix_info_data', 'info', 'data')
    )
    child = Table(
        CHILD_TABLE, metadata,
        Column('id', Integer, primary_key=True),
        Column('parent_id', Integer, ForeignKey(f'{SCHEMA_NAME}.{PARENT_TABLE}.id', ondelete='CASCADE')),
        Column('value', String(50))
    )
    metadata.drop_all(engine)
    metadata.create_all(engine)
    yield parent, child
    metadata.drop_all(engine)

def test_foreign_key_and_cascade(setup_advanced_schema):
    engine = create_engine(DATABASE_URL)
    parent, child = setup_advanced_schema
    with Session(engine) as session:
        p = parent.insert().values(info='parent', data={"foo": 1}, tags=['a', 'b'])
        p_id = session.execute(p).inserted_primary_key[0]
        session.execute(child.insert().values(parent_id=p_id, value='child1'))
        session.commit()
        # Delete parent, child should be deleted (cascade)
        session.execute(parent.delete().where(parent.c.id == p_id))
        session.commit()
        c = session.execute(child.select().where(child.c.parent_id == p_id)).fetchone()
        assert c is None

def test_composite_index(setup_advanced_schema):
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        # Index should exist
        result = conn.execute(text(f"SELECT indexname FROM pg_indexes WHERE schemaname = :schema AND tablename = :table;"), {"schema": SCHEMA_NAME, "table": PARENT_TABLE})
        indexes = [row[0] for row in result.fetchall()]
        assert any('ix_info_data' in idx for idx in indexes)

def test_jsonb_and_array_types(setup_advanced_schema):
    engine = create_engine(DATABASE_URL)
    parent, _ = setup_advanced_schema
    with Session(engine) as session:
        ins = parent.insert().values(info='jsonb', data={"bar": [1,2]}, tags=['x','y'])
        row_id = session.execute(ins).inserted_primary_key[0]
        session.commit()
        sel = parent.select().where(parent.c.id == row_id)
        row = session.execute(sel).fetchone()
        assert row['data']['bar'] == [1,2]
        assert row['tags'] == ['x','y']

def test_permissions_and_error():
    # Try to connect with a non-existent user
    with pytest.raises(Exception):
        psycopg2.connect(dbname=DB_NAME, user='nouser', password='bad', host=DB_HOST, port=DB_PORT)

def test_concurrent_access(setup_advanced_schema):
    import threading
    engine = create_engine(DATABASE_URL)
    parent, _ = setup_advanced_schema
    def insert_row(val):
        with Session(engine) as session:
            session.execute(parent.insert().values(info=val, data={}, tags=[]))
            session.commit()
    threads = [threading.Thread(target=insert_row, args=(f"t{i}",)) for i in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    with Session(engine) as session:
        count = session.execute(parent.count()).scalar()
        assert count >= 5

def test_performance_bulk_insert(setup_advanced_schema):
    engine = create_engine(DATABASE_URL)
    parent, _ = setup_advanced_schema
    with Session(engine) as session:
        objs = [{"info": f"bulk{i}", "data": {}, "tags": []} for i in range(100)]
        session.execute(parent.insert(), objs)
        session.commit()
        count = session.execute(parent.count()).scalar()
        assert count >= 100
