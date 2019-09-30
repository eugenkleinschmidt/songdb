import argparse

from songdb import SongDB


def main():
    args = argparse.ArgumentParser(prog='songdb')
    args.add_argument('song', help='song name')
    args.add_argument('lasttime', help='date when song is performed')

    args = args.parse_args()

    sdb = SongDB()
    print('Song included into DB', args.song,  args.lasttime)
    sdb.new_song_performance(args.song, args.lasttime)


if __name__ == '__main__':
    main()
