from songdb import SongDB
from datetime import date


class TestSongDB(object):
    def test_new_song_entry(self):
        sbd = SongDB()
        sbd.new_song_performance("Heilig", date.today().isoformat())
