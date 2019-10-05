import datetime
import os
import shutil

import pytest
from cli import main
from tinydb import where

from songdb import SongDB


def this_path(path):
    return os.path.join(os.path.split(__file__)[0], path)


def current_test_name():
    return os.environ.get('PYTEST_CURRENT_TEST').split(':')[-1].split(' ')[0]


def unpack_test_data(tmpdir):
    temp = tmpdir.mkdir(current_test_name())
    shutil.unpack_archive(this_path('test_path.zip'), temp)
    return str(temp)


def test_new_song_entry(db):
    today = datetime.datetime.today().date().strftime('%d.%m.%Y')

    with SongDB() as sdb:  # close needed as cachedmiddle used --> context manager
        sdb.new_song_entry("Heilig", today)
    assert today in db.get(where('song') == 'Heilig')['last_time']
    assert db.get(where('song') == 'Heilig')['cnt'] == 1

    with SongDB() as sdb:
        sdb.new_song_entry("New_Song")
    assert db.get(where('song') == 'New_Song')['last_time'] is None
    assert db.get(where('song') == 'New_Song')['cnt'] == 0

    with SongDB() as sdb:
        sdb.new_song_entry("New_Song", "01.02.2134")
    assert "01.02.2134" in db.get(where('song') == 'New_Song')['last_time']
    assert db.get(where('song') == 'New_Song')['cnt'] == 1

    with SongDB() as sdb:
        sdb.new_song_entry("New_Song", "01.02.2020")
    assert "01.02.2134" in db.get(where('song') == 'New_Song')['last_time']
    assert db.get(where('song') == 'New_Song')['cnt'] == 2


def test_get_song_entry(db):
    sdb = SongDB()
    song_entry = sdb.get_song_entry('Heilig1')
    assert song_entry == []

    song_entry = sdb.get_song_entry('Heilig2')
    assert song_entry[0]['song'] == 'Heilig2'


def test_list_from_folder(db, tmpdir):
    sdb = SongDB()
    songlist = sdb.list_from_folder(unpack_test_data(tmpdir))
    assert 'Alles will ich Jesu weihen' in songlist


def test_import_songs(db):
    with open(this_path('test_songdb.txt'), 'r') as f:
        songs = [song.split()[0] for song in f]

    with SongDB() as sdb:
        sdb.import_songs(songs)
    assert db.get(where('song') == 'HeiligWO5')['last_time'] is None
    assert db.get(where('song') == 'HeiligWO5')['cnt'] == 0


def test_validate_date():
    assert SongDB.validate_date(
        datetime.datetime.today().date().strftime('%d.%m.%Y')) == datetime.datetime.today().date()
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
    # TODO find out how to pass arguments to argparse
    # https://stackoverflow.com/questions/18160078/how-do-you-write-tests-for-the-argparse-portion-of-a-python-module
    import sys
    sys.argv.append('01.01.2019')
    main()
    assert '01.01.2019' in db.get(where('song') == 'test_songdb.py::test_main')['last_time']
    assert db.get(where('song') == 'test_songdb.py::test_main')['cnt'] == 1


def test_cmd_new_song(db):
    os.system('songdb --new_song "Test Song" --date 01.02.3456')
    assert '01.02.3456' in db.get(where('song') == 'Test Song')['last_time']
    assert db.get(where('song') == 'Test Song')['cnt'] == 1

    os.system('songdb --new_song "Test Song2"')
    assert db.get(where('song') == 'Test Song2')['last_time'] is None
    assert db.get(where('song') == 'Test Song2')['cnt'] == 0


def test_cmd_file(db):
    os.system('songdb --file ' + this_path('test_songdb.txt'))
    assert db.get(where('song') == 'HeiligWO5')['last_time'] is None
    assert db.get(where('song') == 'HeiligWO5')['cnt'] == 0


def test_cmd_folder(db, tmpdir):
    os.system('songdb --path ' + unpack_test_data(tmpdir))
    assert db.get(where('song') == 'Alles will ich Jesu weihen')['last_time'] is None
    assert db.get(where('song') == 'Alles will ich Jesu weihen')['cnt'] == 0
