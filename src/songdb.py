import os
from datetime import date
from datetime import datetime

from tinydb import Query
from tinydb import TinyDB
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import JSONStorage
from tinydb_serialization import SerializationMiddleware
from tinydb_serialization import Serializer

DATE_FORMAT = '%d.%m.%Y'


class DateTimeSerializer(Serializer):
    OBJ_CLASS = date  # The class this serializer handles

    def encode(self, obj):
        return obj.strftime(DATE_FORMAT)

    def decode(self, s):
        return datetime.strptime(s, DATE_FORMAT).date()


class SongDB(object):
    SONG_DB_PATH = 'songdb.json'

    def __init__(self, db=SONG_DB_PATH):
        serialization = SerializationMiddleware(CachingMiddleware(JSONStorage))
        serialization.register_serializer(DateTimeSerializer(), 'TinyDate')

        self._db = TinyDB(db, storage=serialization, sort_keys=True, indent=4,
                          separators=(',', ': '))
        self._query = Query()

    @staticmethod
    def _update_song_entry(last_time):
        def transform(doc):
            doc['cnt'] += 1
            if doc['last_time']:
                doc['last_time'] = SongDB.compare_date(doc['last_time'], last_time)
            else:
                doc['last_time'] = last_time  # First update after new insert

        return transform

    @staticmethod
    def validate_date(date_text):
        try:
            return datetime.date(datetime.strptime(date_text, DATE_FORMAT))
        except ValueError:
            raise ValueError("Incorrect data format, should be DD.MM.YYYY. e.g. 01.01.2019")

    @staticmethod
    def compare_date(date1, date2):
        latest_date = date1 if date1 >= date2 else date2
        return latest_date

    def new_song_entry(self, song, last_time=None):

        loc_date = SongDB.validate_date(last_time) if last_time else date.today()

        if self._db.contains(self._query.song == song):
            print('Update song:', song, loc_date.strftime(DATE_FORMAT))
            self._db.update(self._update_song_entry(loc_date), self._query.song == song)
        else:
            print('New song:', song, loc_date.strftime(DATE_FORMAT) if last_time else 'No date')
            self._db.insert({'song': song, 'cnt': 1 if last_time else 0, 'last_time': loc_date if last_time else None})

    def get_song_entry(self, song):
        return self._db.search(self._query.song == song)

    def import_songs(self, songs=list):
        for song in songs:
            if not self.get_song_entry(song):
                self.new_song_entry(song)

    @staticmethod
    def list_from_folder(path, ext='.pdf'):
        songs = []
        for root, dir, files in os.walk(path):
            for file in files:
                if file.lower().endswith(ext):
                    song = os.path.splitext(file)[0]
                    if song not in songs:
                        songs.append(song)
        return songs

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._db.close()
