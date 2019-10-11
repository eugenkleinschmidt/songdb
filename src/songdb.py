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


class SongDB(TinyDB):
    SONG_DB_PATH = 'songdb.json'

    def __init__(self, db=SONG_DB_PATH):
        CachingMiddleware.WRITE_CACHE_SIZE = 100000  # For context manager to be on save sight to make a cache clear
        serialization = SerializationMiddleware(CachingMiddleware(JSONStorage))
        serialization.register_serializer(DateTimeSerializer(), 'TinyDate')

        super().__init__(db, storage=serialization, sort_keys=True, indent=4,
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

    def new_song_entry(self, song, last_date=None):

        loc_date = SongDB.validate_date(last_date) if last_date else date.today()

        if self.contains(self._query.song == song):
            print('Update song:', song, loc_date.strftime(DATE_FORMAT))
            self.update(self._update_song_entry(loc_date), self._query.song == song)
        else:
            print('New song:', song, loc_date.strftime(DATE_FORMAT) if last_date else 'No date')
            self.insert({'song': song, 'cnt': 1 if last_date else 0, 'last_time': loc_date if last_date else None})

    def get_song_entry(self, song):
        return self.search(self._query.song == song)

    def import_songs(self, songs=list):
        for song in songs:
            if not self.get_song_entry(song):
                self.new_song_entry(song)

    def update_songs(self, songs=dict):
        for song, last_date in songs.items():
            self.new_song_entry(song, last_date)

    @staticmethod
    def list_from_folder(path, ext='.pdf') -> list:
        songs = []
        for root, dir, files in os.walk(path):
            for file in files:
                if file.lower().endswith(ext):
                    song = os.path.splitext(file)[0]
                    if song not in songs:
                        songs.append(song)
        return songs

    def clear_cache(self):
        # Serializer Middleware
        self.storage._cache_modified_count = 0
        self.storage.cache = None
        # Caching Middleware
        self.storage.storage._cache_modified_count = 0
        self.storage.storage.cache = None
