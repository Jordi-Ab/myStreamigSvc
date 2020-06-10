from google_drive_svc import GoogleDrive

import io
from pydub import AudioSegment
import subprocess
import pickle
from tempfile import NamedTemporaryFile
from tempfile import TemporaryDirectory
import os

GD_SVC = GoogleDrive()

def play_song(audio_seg, player='vlc'):
    print('playing song ...')
    if player == 'vlc':
        command = "/Applications/VLC.app/Contents/MacOS/VLC"
    elif player == 'ffplay':
        command = player
    else:
        raise ValueError('Only "vlc" and "ffplay" as currently supported.')
    
    with NamedTemporaryFile("w+b", suffix=".wav") as f:
        song.export(f.name, 'wav')
        proc = subprocess.call([command, f.name])

def glue_songs(files_dict):
    print('gluing songs together ...')
    glued_songs = AudioSegment.empty()
    for name, audio_seg in files_dict.items():        
        glued_songs += audio_seg
    return glued_songs

def play_files_continuously(files_dict, play_with = 'vlc'):
    glued_songs=glue_songs(files_dict)
    play_song(glued_songs, player=play_with)

def play_files_as_playlist(files):
    # create the playlist
    with TemporaryDirectory() as td:
        f_names = [os.path.join(td, f'{n}') for n in files.keys()]
        print('exporting playlist to temp file ...')
        with open(os.path.join(td,'playlist.m3u'), 'w+t') as playlist:
            for name in f_names:
                song_name = name.split('/')[-1]
                audio_seg = files[song_name]
                playlist.writelines([name+'.wav\n'])
                with open(name+'.wav', 'w+b') as tempsong:
                    audio_seg.export(tempsong.name, 'wav')
        
        print('Playing on VLC ...')
        proc = subprocess.call(
            ["/Applications/VLC.app/Contents/MacOS/VLC", playlist.name]
        )

def to_pydub_audiosegment(song_names, drive_songs_dict, drive_service):
    print('No data about current album. Creating data ...')
    files = {}
    for n in song_names:
        for f in drive_songs_dict:
            if f['name'] == n:

                song_name = n.split('.')[0]
                file_fmt = n.split('.')[-1]

                file_data = drive_service.open_file(file_id=f['id'])
                song = AudioSegment.from_file(
                    io.BytesIO(file_data), 
                    format=file_fmt
                )
                files[song_name] = song
    return files
        
def create_and_upload_songs_audio_segments(
    song_names, 
    drive_songs_dict, 
    drive_service,
    chosen_album
):
    songs_info = to_pydub_audiosegment(song_names, drive_songs_dict)
    with TemporaryDirectory() as td:
        with open(os.path.join(td,'songs_data.pickle'), 'wb') as handle:
            pickle.dump(songs_info, handle)

        print('Uploading data to Google Drive ...')
        drive_service.upload_file(
            full_path_to_file=os.path.join(td,'songs_data.pickle'),
            drive_file_name='songs_data.pickle', 
            mimetype=None,
            parent_folders_ids = [chosen_album['id']]
        )

def launch_vlc_with_selection(
    chosen_album, 
    drive_service,
    files_inside_drive,
    song_names
):
    files_inside_drive = drive_service.list_files_on_folder(chosen_album['id'])
    song_names = sorted(
        [
            f['name'] for f in files_inside_drive if f['name'].split('.')[-1] in SONG_FORMATS
        ]
    )

    song_info = get_songs_audio_segments(song_names, files_inside_drive)
    play_files_as_playlist(song_info)
