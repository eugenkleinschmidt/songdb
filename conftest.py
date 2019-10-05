import pytest
from tinydb import TinyDB

DB_PATH = 'songdb.json'

DB = (
    {'song': 'Heilig', 'cnt': 0, 'last_time': None},
    {'song': 'Heilig2', 'cnt': 1, 'last_time': '01.01.2019'},
    {'song': 'Heilig3', 'cnt': 2, 'last_time': '01.01.2019'},
)


@pytest.fixture
def db():
    db = TinyDB(DB_PATH, sort_keys=True, indent=4, separators=(',', ': '))
    db.purge_tables()
    db.insert_multiple(DB)
    return db
