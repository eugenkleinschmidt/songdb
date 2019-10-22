import os
from datetime import date

import mock
import setlist.cli
from setlist.setlist import SetList
from songdb.songdb import SongDB

song = ['HALLO', 'HALLO', 'HALLO', 'HALLO', 'HALLO', 'HALLO', 'HALLO', 'HALLO', 'HALLO', 'HALLO']


def this_path(path):
    return os.path.join(os.path.split(__file__)[0], path)


def current_test_name():
    return os.environ.get('PYTEST_CURRENT_TEST').split(':')[-1].split(' ')[0]


def test_setlist():
    pList = SetList()

    pList.date(date.today())
    pList.song(song[0], link='www.web.de')

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


def test_new_setlist(db):
    pList = SetList()
    pList.new_setlist('01.02.3456', [['Anbetung', 'Heilig'], ])
    db = SongDB()
    assert db.get_song_entry('Heilig')[0]['last_time'] == db.validate_date('01.02.3456')


@mock.patch('setlist.cli.argparse')
def test_cli(mock_argparse):
    class mock_args():
        date = '01.01.2019'
        song_group = [['Lobpreis', 'Neues Lied', 'Zweites Neues Lied'], ]
        force = True

    with mock.patch.object(setlist.cli.argparse.ArgumentParser(), 'parse_args', return_value=mock_args):
        setlist.cli.main()


def test_cmd(db):
    os.system('setlist --date 01.02.3456 --song-group Anbetung Heilig')
    db = SongDB()
    assert db.get_song_entry('Heilig')[0]['last_time'] == db.validate_date('01.02.3456')


def test_cmd_not_available_song(db):
    os.system('setlist --date 01.02.3456 --song-group Anbetung "Test New Song"')
    db = SongDB()
    assert db.get_song_entry('Test New Song') == []


def test_cmd_help():
    os.system('setlist')
