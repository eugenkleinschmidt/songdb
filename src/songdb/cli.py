import argparse

from .songdb import SongDB, import_songs, list_from_folder, splitline_from_file


def main():
    args = argparse.ArgumentParser(prog='songdb')
    option = args.add_mutually_exclusive_group(required=True)
    option.add_argument('--file', help='CVS file with songs (\n , ; separated)')
    option.add_argument('--path', help='folder with song files (comma separated)')
    option.add_argument('--new_song', help='Song name of one new song')
    args.add_argument('--link', required=False, help='link to song e.g youtube')
    args.add_argument('--sheet', required=False, help='path to music sheet')
    args.add_argument('--ext', required=False, default='.pdf', help='file extensions in folder (only for option --path)')

    args = args.parse_args()

    with SongDB() as sdb:
        if args.file:
            print('Importing songs into DB from', args.file)
            with open(args.file, 'r') as f:
                with SongDB() as sdb:
                    import_songs(sdb, splitline_from_file(f))
        elif args.path:
            print('Importing songs into DB from', args.path)
            import_songs(sdb, list_from_folder(args.path, args.ext))
        else:
            sdb.new_song_entry(args.new_song, args.link, args.sheet)
