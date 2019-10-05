import argparse

from songdb import SongDB


def main():
    args = argparse.ArgumentParser(prog='songdb')
    option = args.add_mutually_exclusive_group(required=True)
    option.add_argument('--file', help='CVS file with songs (\n , ; separated)')
    option.add_argument('--path', help='folder with song files (comma separated)')
    option.add_argument('--new_song', help='Song name of one new song')
    args.add_argument('--date', required=False, help='date when song is performed (only for option --new)')
    args.add_argument('--ext', required=False, default='.pdf', help='file extensions in folder (only for option --path)')

    args = args.parse_args()

    with SongDB() as sdb:
        if args.file:
            print('Importing songs into DB from', args.file)
            with open(args.file, 'r') as f:
                if ',' in f.readline():
                    songs = {song.split(',')[0]: song.split(',')[1].split()[0] for song in f}
                    sdb.update_songs(songs)
                else:
                    songs = [line.split()[0] for line in f]
                    sdb.import_songs(songs)

        elif args.path:
            print('Importing songs into DB from', args.path)
            sdb.import_songs(sdb.list_from_folder(args.path, args.ext))
        if args.new_song:
            if args.date:
                print('Including used song into DB')
                sdb.new_song_entry(args.new_song, args.date)
            else:
                print('Including new song into DB')
                sdb.new_song_entry(args.new_song)
