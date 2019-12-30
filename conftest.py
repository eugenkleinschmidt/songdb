import subprocess
import pytest
from tinydb import TinyDB

DB_PATH = 'songdb.json'

DB = (
    {'song': 'Heilig', 'link': 0, 'sheet': None},
    {'song': 'Heilig2', 'link': 1, 'sheet': '01.01.2019'},
    {'song': 'Heilig3', 'link': 2, 'sheet': '01.01.2019'},
)


@pytest.fixture
def db():
    db = TinyDB(DB_PATH, sort_keys=True, indent=4, separators=(',', ': '))
    db.purge_tables()
    db.insert_multiple(DB)
    return db


def check_installed():
    try:
        subprocess.run('setlist')
        subprocess.run('songdb')
    except FileNotFoundError:
        return False
    else:
        return True
