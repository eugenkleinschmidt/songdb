import argparse

from .setlist import SetList


def main():
    args = argparse.ArgumentParser(prog='setlist')
    args.add_argument('-d', '--date', required=True, help='date of setlist')
    args.add_argument('-sg', '--song-group', required=True, action='append', nargs='*',
                      help='group of songs. First comes the name of the group')
    args.add_argument('-f', '--force', action='store_true', help='force if songs are new')

    args = args.parse_args()

    sl = SetList()
    sl.new_setlist(args.date, args.song_group, args.force)
