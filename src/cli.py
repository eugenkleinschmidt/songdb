import argparse

from songdb import SongDB


def main():
    args = argparse.ArgumentParser(prog='songdb')
    args.add_argument('song', help='song name')
    args.add_argument('lasttime', nargs='?', help='date when song is performed')

    args = args.parse_args()

    sdb = SongDB()
    print('Including song into DB\n\tSongname:', args.song, '\tDate:', args.lasttime)
    sdb.new_song_entry(args.song, args.lasttime)
