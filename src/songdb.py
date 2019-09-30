from tinydb import TinyDB, Query
from tinydb.operations import increment
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware


class SongDB(object):
    def __init__(self):
        self._db = TinyDB('songdb.json', storage=CachingMiddleware(JSONStorage))

    @staticmethod
    def _update_song_entry(last_time):
        def transform(doc):
            doc['cnt'] += 1
            doc['last_time'] = last_time

        return transform

    def new_song_performance(self, song, last_time):
        print('New song:', song, last_time)
        with self._db as db:
            song_entry = Query()
            if db.contains(song_entry.song == song):
                db.update(increment('cnt'), )
            else:
                db.insert({'song': song, 'cnt': 0, 'last_time': last_time})

    def __del__(self):
        self._db.close()
