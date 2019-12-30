import PySimpleGUI as sg
# import PySimpleGUIWeb as sg

from songdb.songdb import SongDB as sdb
# from setlist.setlist import SetList as sl


class SongDbGui(object):
    def __init__(self):

        new_song_layout = [
            [sg.Text('Songname'), sg.Input(key='i_songname')],
            [sg.Text('Link'), sg.Input(key='i_link')],
            [sg.Button('Enter'), sg.Exit()]
        ]

        window = sg.Window('Song DB', new_song_layout)

        while True:  # The Event Loop
            event, values = window.read()

            if event == 'Enter':
                sdb.new_song_entry(values['i_songname'], values['i_link'])

            # close programm
            if event in (None, 'Exit'):
                break

        window.close()


if __name__ == '__main__':
    SongDbGui()
