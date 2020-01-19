import os
import subprocess

import pytest
from tinydb import TinyDB

DB_PATH = 'songdb.json'

DB = (
    {'song': 'Heilig', 'link': 0, 'sheet': None},
    {'song': 'Heilig2', 'link': 1, 'sheet': None, 'dates': ['01.01.2019', ]},
    {'song': 'Heilig3', 'link': 2, 'sheet': 'das/ist/ein/pfad', 'dates': ['01.01.2019', ]},
)


def this_path(path):
    return os.path.join(os.path.split(__file__)[0], path)


def current_test_name():
    return os.environ.get('PYTEST_CURRENT_TEST').split(':')[-1].split(' ')[0]


@pytest.fixture
def db():
    db = TinyDB(DB_PATH, sort_keys=True, default_table='songs', indent=4, separators=(',', ': '))
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
