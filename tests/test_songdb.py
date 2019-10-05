import datetime

import pytest
from cli import main
from tinydb import where

from songdb import SongDB


def test_new_song_entry(db):
    today = datetime.datetime.today().date().strftime('%d.%m.%Y')

    with SongDB() as sbd:
        sbd = SongDB()
        sbd.new_song_entry("Heilig", today)
    assert today in db.get(where('song') == 'Heilig')['last_time']
    assert db.get(where('song') == 'Heilig')['cnt'] == 1

    with SongDB() as sbd:
        sbd.new_song_entry("New_Song")
    assert db.get(where('song') == 'New_Song')['last_time'] is None
    assert db.get(where('song') == 'New_Song')['cnt'] == 0

    with SongDB() as sbd:
        sbd.new_song_entry("New_Song", "01.02.2134")
    assert "01.02.2134" in db.get(where('song') == 'New_Song')['last_time']
    assert db.get(where('song') == 'New_Song')['cnt'] == 1

    with SongDB() as sbd:
        sbd.new_song_entry("New_Song", "01.02.2020")
    assert "01.02.2134" in db.get(where('song') == 'New_Song')['last_time']
    assert db.get(where('song') == 'New_Song')['cnt'] == 2


def test_get_song_entry(db):
    sbd = SongDB()
    song_entry = sbd.get_song_entry('Heilig1')
    assert song_entry == []

    song_entry = sbd.get_song_entry('Heilig2')
    assert song_entry[0]['song'] == 'Heilig2'


def test_validate_date():
    assert SongDB.validate_date(datetime.datetime.today().date().strftime('%d.%m.%Y')) == datetime.datetime.today().date()
    assert SongDB.validate_date('01.01.2019')

    with pytest.raises(ValueError):
        SongDB.validate_date('01.01.19')
    with pytest.raises(ValueError):
        SongDB.validate_date('40.01.2019')
    with pytest.raises(ValueError):
        SongDB.validate_date('01.40.2019')
    with pytest.raises(ValueError):
        SongDB.validate_date('01.01.10000')


def test_compare_date():
    d1 = datetime.date(2019, 1, 1)
    d2 = datetime.date(2019, 1, 2)
    assert SongDB.compare_date(d1, d2) == d2


@pytest.mark.skip('Not run in tox because of passed arguments')
def test_main(db):
    import sys
    sys.argv.append('01.01.2019')
    main()
    assert '01.01.2019' in db.get(where('song') == 'test_songdb.py::test_main')['last_time']
    assert db.get(where('song') == 'test_songdb.py::test_main')['cnt'] == 1


def test_cmd(db):
    import os
    os.system('songdb "TestSong" 01.02.3456')
    assert '01.02.3456' in db.get(where('song') == 'TestSong')['last_time']
    assert db.get(where('song') == 'TestSong')['cnt'] == 1
