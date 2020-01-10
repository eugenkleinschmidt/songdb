import argparse

from .setlist import Setlist, SetlistDB


def main():
    args = argparse.ArgumentParser(prog='setlist')
    args.add_argument('-n', '--name', required=True, help='name of setlist')
    args.add_argument('-d', '--date', required=True, help='date of setlist')
    option = args.add_mutually_exclusive_group(required=True)
    option.add_argument('-sg', '--song-group', action='append', nargs='*',
                        help='group of songs. First comes the name of the group')
    option.add_argument('-v', '--validate', help='Update songs from this setlist with new dates')

    args = args.parse_args()

    sl = Setlist()
    sl.new_setlist(args.name, args.date, args.song_group)

    loc_songs = []
    for sg in args.song_group:
        for s in sg[1:]:
            loc_songs.append(s)

    if args.validate:
        with SetlistDB as sldb:
            sldb.validate_setlist(args.name, args.date)
    else:
        with SetlistDB() as sldb:
            sldb.new_setlist_entry(args.name, args.date, loc_songs)
