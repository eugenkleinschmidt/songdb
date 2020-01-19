import os
import typing
from datetime import date, datetime

from tinydb import Query, TinyDB
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import JSONStorage
from tinydb_serialization import SerializationMiddleware, Serializer

from .utils import get_logger

DATE_FORMAT = '%d.%m.%Y'


# TODO currently not use maybe remove it?
class DateTimeSerializer(Serializer):
    OBJ_CLASS = date  # The class this serializer handles

    def encode(self, obj):
        return obj.strftime(DATE_FORMAT)  # pragma: no cover

    def decode(self, s):
        return datetime.strptime(s, DATE_FORMAT).date()  # pragma: no cover


log = get_logger()


class SongDB(TinyDB):
    SONG_DB_DEFAULT_PATH = 'songdb.json'

    def __init__(self, db=SONG_DB_DEFAULT_PATH):
        CachingMiddleware.WRITE_CACHE_SIZE = 100000  # For context manager to be on save sight to make a cache clear
        serialization = SerializationMiddleware(CachingMiddleware(JSONStorage))
        serialization.register_serializer(DateTimeSerializer(), 'TinyDate')

        super().__init__(db, storage=serialization, default_table='songs', sort_keys=True, indent=4,
                         separators=(',', ': '))

        self.query = Query()

    @staticmethod
    def validate_date(date_text: str):
        try:
            return datetime.date(datetime.strptime(date_text, DATE_FORMAT))
        except ValueError:
            log.error('Incorrect data format, should be DD.MM.YYYY. e.g. 01.01.2019')
            raise ValueError('Incorrect data format, should be DD.MM.YYYY. e.g. 01.01.2019')

    @staticmethod
    def compare_date(date1, date2):
        latest_date = date1 if date1 >= date2 else date2
        return latest_date

    def new_song_entry(self, song: str, link: str = None, sheet: str = None):
        """
        Create or update an a song. Update means new link or sheet path
        :param song: Songname
        :param link: Link to song example e.g. youtube
        :param sheet: Path to music sheet
        :return:
        """
        if self.contains(self.query.song == song):
            if not link and not sheet:  # pragma: no cover
                log.warning(f'Song {song} already in DB. No addition information given')  # pragma: no cover
            log.info(f'Update song {song}. \n\tLink: {link}\n\tSheet: {sheet}')
        else:
            log.info(f'New song {song}.')
        self.upsert({'song': song, 'link': link, 'sheet': sheet}, self.query.song == song)

    def update_song_date(self, song: str, setlist_date: str):
        """
        Insert or update song dates when song was performed.
        :param song: songname
        :param setlist_date: date when song is/was performed
        :return:
        """
        loc_song = self.search(self.query.song == song)
        if loc_song and len(loc_song) == 1:  # pragma: no cover
            loc_song = loc_song[0]
            loc_date = SongDB.validate_date(setlist_date) if setlist_date else date.today()
            log.info(f'New date {loc_date.strftime(DATE_FORMAT)} for song {loc_song["song"]}')
            if 'dates' in loc_song:
                loc_song['dates'].append(setlist_date)
                loc_song['dates'].sort(reverse=True)
            else:
                loc_song['dates'] = [setlist_date, ]
            self.write_back([loc_song, ])
        else:
            # TODO or to many found
            log.warning(f'Song {song} not in DB. No update of dates.')  # pragma: no cover

    def get_song_dates(self, song: str):
        return self.search((self.query.song == song) & (self.query.dates.exists()))[0]['dates']

    def get_song_entry(self, song: str):
        return self.search(self.query.song == song)

    def clear_cache(self):
        # Serializer Middleware
        self.storage._cache_modified_count = 0
        self.storage.cache = None
        # Caching Middleware
        self.storage.storage._cache_modified_count = 0
        self.storage.storage.cache = None


# Helper Functions
def splitline_from_file(file_obj: typing.TextIO):
    return [line.rstrip('\n').split(',') for line in file_obj]


def import_songs(sdb: SongDB, songs: list):
    """
    Updating songs from list of list (song, link, sheet)
    :param sdb: instance of SongDB
    :param songs: list of songs
    :return:
    """
    for song in songs:
        if isinstance(song, list):
            if len(song) <= 3:  # pragma: no cover
                sdb.new_song_entry(*song)
            else:
                raise TypeError(f'new song has to much elements {song}')  # pragma: no cover
        else:
            sdb.new_song_entry(song)


def list_from_folder(path, ext='.pdf') -> list:
    """
    Returns list of songs from folder path with matching extension
    :param path: Path to folder with songs files
    :param ext: Extention of song files
    :return: List of songs
    """
    songs = []
    for root, dir, files in os.walk(path):
        for file in files:
            if file.lower().endswith(ext):
                song = os.path.splitext(file)[0]
                if song not in songs:  # pragma: no cover
                    songs.append(song)
    return songs
