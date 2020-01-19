from fpdf import FPDF

from songdb.songdb import SongDB


class Setlist(FPDF):
    COLOR_VIOLET = (150, 50, 100)

    def __init__(self):
        super().__init__('P', 'mm', 'A4')
        self.add_page()
        self.set_margins(left=25, top=30)
        self.set_font('Arial', size=16)

    def date(self, date):
        self.set_text_color(1, 1, 1)
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, str(date), 0, ln=1, align='C')
        self.ln()
        self.ln()

    def group(self, text, color=COLOR_VIOLET):
        self.ln()
        self.set_text_color(*color)
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, text, 0, ln=1)

    def song(self, text, link=None):
        self.set_text_color(1, 1, 1)
        self.set_font('Arial', size=16)
        self.cell(20)
        self.cell(0, 10, text, 0, ln=1, link=link)

    def new_setlist(self, name: str, date: str, song_groups: list):
        """
        Create new PDF Setlist for given date. Song groups are in order --> group title then all songs.
        :param name: name of setlist
        :param date: planned date for setlist
        :param song_groups: list of song groups.
        :return: None
        """
        self.date(date if SongDB.validate_date(date) else '')
        for sg in song_groups:
            self.group(sg[0])
            for s in sg[1:]:
                with SongDB() as sdb:
                    if not sdb.get_song_entry(s):  # pragma: no cover
                        pass  # log.warning(f'Song {s} not in database)
                self.song(s)
        self.output(f'Setlist_{date}.pdf')


class SetlistDB(object):

    def __init__(self, db: str = SongDB.SONG_DB_DEFAULT_PATH):
        self.sdb = SongDB(db)
        self.sldb = self.sdb.table('setlists')

    def new_setlist_entry(self, name: str, date: str, songs: list):
        """
        Create or update an a song. Update means new link or sheet path
        :param name: name of setlist
        :param date: date of setlist
        :param songs: list of songs
        :return: setlist name and date as kinda setlist id
        """
        if self.sldb.contains((self.sdb.query.setlist == name) & (self.sdb.query.date == date)):  # pragma: no cover
            # log.info(f'Update setlist {name} for date {date} with new songs. \n\tSongs: {songs}')
            self.sldb.upsert({'setlist': name, 'date': date, 'songs': songs},  # pragma: no cover
                             (self.sdb.query.setlist == name) & (self.sdb.query.date == date))
        else:
            # log.info(f'New setlist {name} for date {date} with songs. \n\tSongs: {songs}')
            self.sldb.insert({'setlist': name, 'date': date, 'songs': songs})
        return name, date

    def get_setlist_entry(self, name: str, date: str):
        return self.sldb.search((self.sdb.query.setlist == name) & (self.sdb.query.date == date))

    def validate_setlist(self, name: str, date: str):
        """
        All songs of

        :param name: name of setlist
        :param date: date of setlist
        :return:
        """

        loc_sl = self.sldb.search((self.sdb.query.setlist == name) & (self.sdb.query.date == date))
        if len(loc_sl) == 1:  # pragma: no cover
            for s in loc_sl[0]['songs']:
                if self.sdb.get_song_entry(s):
                    # TODO logging
                    self.sdb.update_song_date(s, date)
                else:
                    self.sdb.new_song_entry(s)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.sdb._opened:  # pragma: no cover
            self.sdb.close()
