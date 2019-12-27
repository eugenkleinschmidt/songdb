import os
from datetime import date, datetime

from .utils import get_logger

from tinydb import Query, TinyDB
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import JSONStorage
from tinydb_serialization import SerializationMiddleware, Serializer

DATE_FORMAT = '%d.%m.%Y'


class DateTimeSerializer(Serializer):
    OBJ_CLASS = date  # The class this serializer handles

    def encode(self, obj):
        return obj.strftime(DATE_FORMAT)

    def decode(self, s):
        return datetime.strptime(s, DATE_FORMAT).date()


log = get_logger()


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
    def validate_date(date_text: str):
        try:
            return datetime.date(datetime.strptime(date_text, DATE_FORMAT))
        except ValueError:
            raise ValueError("Incorrect data format, should be DD.MM.YYYY. e.g. 01.01.2019")

    @staticmethod
    def compare_date(date1, date2):
        latest_date = date1 if date1 >= date2 else date2
        return latest_date

    def new_song_entry(self, song: str, link: str, cheet: str):

        if self.contains(self._query.song == song):
            log('Update song:', song, loc_date.strftime(DATE_FORMAT))
            self.update(self._update_song_entry(loc_date), self._query.song == song)
        else:
            log('New song:', song, loc_date.strftime(DATE_FORMAT) if last_date else 'No date')
            self.insert({'song': song, 'cnt': 1 if last_date else 0, 'last_time': loc_date if last_date else None})

    def update_song_date(self, song: str, setlist_date: str):
        loc_date = SongDB.validate_date(setlist_date) if setlist_date else date.today()

        if self.contains(self._query.song == song):
            log(f'New date {loc_date.strftime(DATE_FORMAT)} for song {song}')
            self.update(self._update_song_entry(loc_date), self._query.song == song)

    def get_song_entry(self, song: str):
        return self.search(self._query.song == song)

    def import_songs(self, songs: list):
        for song in songs:
            if not self.get_song_entry(song):
                self.new_song_entry(song)

    def update_songs(self, songs: dict):
        for song, last_date in songs.items():
            self.new_song_entry(song, last_date)

    @staticmethod
    def list_from_folder(path, ext='.pdf') -> list:
        """
        Create list of songs from folder path with matching extension
        :param path: Path to folder with songs files
        :param ext: Extention of song files
        :return: List of songs
        """
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
