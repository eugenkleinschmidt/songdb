import PySimpleGUI as sg

from songdb.songdb import SongDB as sdb

# import PySimpleGUIWeb as sg
# from setlist.setlist import SetList as sl


class SongDbGui(object):
    PARAM_FILE = '.gui.params'

    def __init__(self):

        new_song_layout = [
            [sg.Text('Song Name'), sg.Input(key='i_songname')],
            [sg.Text('Link'), sg.Input(key='i_link')],
            [sg.Text('Sheet'), sg.Input(key='i_sheet')],
            [sg.Button('Enter')]
        ]

        new_setlist_layout = [
            [sg.Text('Setlist Name'), sg.Input(key='i_setlist')],
            [sg.Text('Date'), sg.Input(key='i_date')],
            [sg.Text('Song'), sg.Input(key='i_song')],
            [sg.Button('Enter')]
        ]

        layout = [
            [sg.TabGroup([[
                sg.Tab('Songs', new_song_layout),
                sg.Tab('Setlist', new_setlist_layout)
                ]]
            )],
            [sg.Button('New Song'), sg.Exit()]
        ]

        window = sg.Window('Song DB', layout, finalize=True)
        window.load_from_disk(self.PARAM_FILE)

        while True:  # The Event Loop
            event, values = window.read()

            if event == 'Enter':
                sdb.new_song_entry(values['i_songname'], values['i_link'])

            # close programm
            if event in (None, 'Exit'):
                break

        window.save_to_disk(self.PARAM_FILE)
        window.close()


if __name__ == '__main__':
    SongDbGui()
