import os
from datetime import date

import mock
import pytest
import setlist.cli as cli
from conftest import check_installed
from setlist.setlist import Setlist, SetlistDB
from songdb.songdb import SongDB
from tinydb import where

song = ['HALLO', 'HALLO', 'HALLO', 'HALLO', 'HALLO', 'HALLO', 'HALLO', 'HALLO', 'HALLO', 'HALLO']


def this_path(path):
    return os.path.join(os.path.split(__file__)[0], path)


def current_test_name():
    return os.environ.get('PYTEST_CURRENT_TEST').split(':')[-1].split(' ')[0]


class TestSetlist(object):
    def test_setlist(self):
        pList = Setlist()

        pList.date(date.today())
        pList.song(song[0], link='https://www.songbeamer.de/download.htm')

        pList.group('Lobpreis')
        pList.song(song[1])
        pList.song(song[2])

        pList.group('Predigt')
        pList.song(song[3])

        pList.group('Abendmahl')
        pList.song(song[5])
        pList.song(song[6])

        pList.group('Spende Ende')
        pList.song(song[7])
        pList.song(song[8])

        pList.output('test_setlist.pdf', 'F')

    def test_new_setlist(self, ):
        pList = Setlist()
        pList.new_setlist('Gottesdienst', '01.02.3456', [['Anbetung', 'Heilig'], ])
        assert os.path.exists('Setlist_01.02.3456.pdf')


class TestSetlistDB(object):

    def test_new_setlist_entry(self, db):
        with SetlistDB() as sldb:
            sl_id = sldb.new_setlist_entry('Gottesdienst', '01.02.3456', ['Heilig', 'Heilig2'])
            sl = sldb.get_setlist_entry(*sl_id)
        assert sl[0]['date'] == '01.02.3456'
        assert db.table('setlists').get(where('setlist') == 'Gottesdienst')['date'] == '01.02.3456'

    def test_validate_setlist(self, db):
        with SetlistDB() as sldb:
            sl_id = sldb.new_setlist_entry('Gottesdienst', '01.02.3456', ['Heilig', 'Heilig2'])
            sldb.validate_setlist(*sl_id)
        assert db.table('songs').get(where('song') == 'Heilig')['dates'] == ['01.02.3456', ]
        assert db.table('songs').get(where('song') == 'Heilig')['dates'][0] == ['01.02.3456', '01.01.2019']


@pytest.mark.skipif(not check_installed(), reason='songdb is not installed. Test skipped')
class TestCmd(object):
    @mock.patch('setlist.cli.argparse')
    def test_cli(self, mock_argparse):
        class mock_args():
            name = 'Gottesdienst'
            date = '01.01.2019'
            song_group = [['Lobpreis', 'Neues Lied', 'Zweites Neues Lied'], ]
            validate = None

        with mock.patch.object(cli.argparse.ArgumentParser(), 'parse_args', return_value=mock_args):
            cli.main()

    def test_cmd(self, db):
        os.system('setlist --name Gottesdienst --date 01.02.3456 --song-group Anbetung Heilig')
        assert db.get(where('setlist') == 'Gottesdienst')['date'] == '01.02.3456'
        # db = SongDB()
        # assert db.get_song_entry('Heilig')[0]['last_time'] == db.validate_date('01.02.3456')

    def test_cmd_not_available_song(db):
        os.system('setlist --name Gottesdienst --date 01.02.3456 --song-group Anbetung "Test New Song"')
        db = SongDB()
        assert db.get_song_entry('Test New Song') == []

    def test_cmd_help(self):
        os.system('setlist')
