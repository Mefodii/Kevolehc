from __future__ import unicode_literals
import time

from icecream import ic

from utils import file
from youtube import paths
from youtube.model.file_extension import FileExtension
from youtube.paths import WATCHERS_DOWNLOAD_PATH
from youtube.utils import db_utils, playlist_utils, media_utils


FILES_VIDEO_ARCHIVE_PATH = "G:\\Filme"
FILES_AUDIO_ARCHIVE_PATH = "G:\\Music\\yt_watchers"


def alter_db_kv():
    files = file.list_files(paths.DB_PATH)
    for item in files:
        db_file = item.get_abs_path()
        ic(db_file)

        data = file.read_json(db_file)

        # change DB keys and values

        file.write_json(db_file, data)


def insert_to_db():
    db_file = "E:\\Coding\\Projects\\Kevolehc\\Kevolehc\\youtube\\files\\_db\\AmbientMusicalGenre.txt"
    video_id = "cMHO685u1tA"
    new_number = 2027
    db_utils.move_video_number(db_file, video_id, new_number)


def shift_playlist():
    playlist_file = "E:\\Google Drive\\Mu\\plist\\AmbientMusicalGenre.txt"
    playlist_utils.shift_number(playlist_file, 2027, 1)


def sync_media():
    db_file = "E:\\Coding\\Projects\\Kevolehc\\Kevolehc\\youtube\\files\\_db\\AmbientMusicalGenre.txt"
    media_paths = [f"{WATCHERS_DOWNLOAD_PATH}\\AmbientMusicalGenre", f"{FILES_AUDIO_ARCHIVE_PATH}\\AmbientMusicalGenre"]
    media_utils.sync_media_filenames_with_db(db_file, media_paths, FileExtension.MP3)


#######################################################################################################################
# Main function
#######################################################################################################################
def __main__():
    pass


#######################################################################################################################
# Process
#######################################################################################################################
if __name__ == "__main__":
    # Start time of the program
    start = time.time()

    # Main functionality
    __main__()

    # End time of the program
    end = time.time()
    # Running time of the program
    print("Program ran for: ", end - start, "seconds.")
