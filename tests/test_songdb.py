import datetime
import os
import shutil

import mock
import pytest
from conftest import check_installed
from songdb import songdb, cli
from tinydb import where

SongDB = songdb.SongDB


def this_path(path):
    return os.path.join(os.path.split(__file__)[0], path)


def current_test_name():
    return os.environ.get('PYTEST_CURRENT_TEST').split(':')[-1].split(' ')[0]


def unpack_test_data(tmpdir):
    temp = tmpdir.mkdir(current_test_name())
    shutil.unpack_archive(this_path('test_path.zip'), temp)
    return str(temp)


today = datetime.datetime.today().date().strftime('%d.%m.%Y')


class TestSongDB(object):
    def test_new_song_entry(self, db):

        with SongDB() as sdb:  # close needed as cachedmiddle used --> context manager
            sdb.new_song_entry("Heilig", today)
        assert today in db.get(where('song') == 'Heilig')['link']
        assert db.get(where('song') == 'Heilig')['sheet'] == 1

        with SongDB() as sdb:
            sdb.new_song_entry("New_Song")
        assert db.get(where('song') == 'New_Song')['link'] is None
        assert db.get(where('song') == 'New_Song')['sheet'] == 0

    def test_update_dates(self, db):
        with SongDB() as sdb:
            sdb.new_song_entry("New_Song", "01.02.2134")
        assert "01.02.2134" in db.get(where('song') == 'New_Song')['link']
        assert db.get(where('song') == 'New_Song')['sheet'] == 1

        with SongDB() as sdb:
            sdb.new_song_entry("New_Song", "01.02.2020")
        assert "01.02.2134" in db.get(where('song') == 'New_Song')['link']
        assert db.get(where('song') == 'New_Song')['sheet'] == 2

    def test_get_song_entry(self, db):
        sdb = SongDB()
        song_entry = sdb.get_song_entry('Heilig1')
        assert song_entry == []

        song_entry = sdb.get_song_entry('Heilig2')
        assert song_entry[0]['song'] == 'Heilig2'

    def test_list_from_folder(self, db, tmpdir):
        sdb = SongDB()
        songlist = sdb.list_from_folder(unpack_test_data(tmpdir))
        assert 'Alles will ich Jesu weihen' in songlist

    def test_import_songs(self, db):
        with open(this_path('test_songdb.txt'), 'r') as f:
            songs = [song.split()[0] for song in f]

        with SongDB() as sdb:
            sdb.import_songs(songs)
        assert db.get(where('song') == 'HeiligWO5')['link'] is None
        assert db.get(where('song') == 'HeiligWO5')['sheet'] == 0

    def test_update_songs(self, db):
        with open(this_path('test_songdb_dates.txt'), 'r') as f:
            songs = {song.split(',')[0]: song.split(',')[1].split()[0] for song in f}

        with SongDB() as sdb:
            sdb.update_songs(songs)
        assert '06.01.2019' in db.get(where('song') == 'HeiligWO5')['link']
        assert db.get(where('song') == 'HeiligWO5')['sheet'] == 1

    def test_clear_cache(self, db):
        with open(this_path('test_songdb_dates.txt'), 'r') as f:
            songs = {song.split(',')[0]: song.split(',')[1].split()[0] for song in f}

        with SongDB() as sdb:
            sdb.update_songs(songs)
            sdb.clear_cache()
        assert db.get(where('song') == 'HeiligWO5') is None

    def test_validate_date(self):
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

    def test_compare_date(self):
        d1 = datetime.date(2019, 1, 1)
        d2 = datetime.date(2019, 1, 2)
        assert SongDB.compare_date(d1, d2) == d2


@pytest.mark.skipif(not check_installed(), reason='songdb is not installed. Test skipped')
class TestCmd(object):

    @mock.patch('songdb.cli.argparse')
    def test_cli(self, mock_argparse):
        class mock_args():
            file = this_path('test_songdb.txt')

        with mock.patch.object(songdb.cli.argparse.ArgumentParser(), 'parse_args', return_value=mock_args):
            cli.main()

    # work only in tox after setup.py installed
    def test_cmd_new_song(self, db):
        os.system('songdb --new_song "Test Song" --date 01.02.3456')
        assert '01.02.3456' in db.get(where('song') == 'Test Song')['link']
        assert db.get(where('song') == 'Test Song')['sheet'] == 1

        os.system('songdb --new_song "Test Song2"')
        assert db.get(where('song') == 'Test Song2')['link'] is None
        assert db.get(where('song') == 'Test Song2')['sheet'] == 0

    def test_cmd_file(self, db):
        os.system('songdb --file ' + this_path('test_songdb.txt'))
        assert db.get(where('song') == 'HeiligWO5')['link'] is None
        assert db.get(where('song') == 'HeiligWO5')['sheet'] == 0

    def test_cmd_file_dates(self, db):
        os.system('songdb --file ' + this_path('test_songdb_dates.txt'))
        assert '06.01.2019' in db.get(where('song') == 'HeiligWO5')['link']
        assert db.get(where('song') == 'HeiligWO5')['sheet'] == 1

    def test_cmd_folder(self, db, tmpdir):
        os.system('songdb --path ' + unpack_test_data(tmpdir))
        assert db.get(where('song') == 'Alles will ich Jesu weihen')['link'] is None
        assert db.get(where('song') == 'Alles will ich Jesu weihen')['sheet'] == 0
