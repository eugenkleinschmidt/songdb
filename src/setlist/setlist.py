from fpdf import FPDF
from songdb.songdb import SongDB


class SetList(FPDF):
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

    def new_setlist(self, date, song_groups: list, force=False):
        """
        Create new PDF Setlist for given date. Song groups are in order --> group title then all songs.
        @param date: planned date for setlist
        @param song_groups: list of song groups.
        @param force: Insert song to database if not existing yet
        @return: None
        """
        with SongDB() as sdb:
            self.date(date if sdb.validate_date(date) else '')
            for sg in song_groups:
                self.group(sg[0])
                for s in sg[1:]:
                    if not force and not sdb.get_song_entry(s):
                        # Clear cache if setlist is wrong and  will not be used
                        # Database must have only songs which are used and reflect only (e.g. song sung on day x times)
                        sdb.clear_cache()
                        raise ValueError('Please insert this song first into your database', s)
                    self.song(s)
                    sdb.new_song_entry(s, date)
            self.output('Setlist_' + date + '.pdf')
