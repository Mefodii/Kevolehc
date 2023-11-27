from __future__ import unicode_literals
import time

from icecream import ic

from utils import file
from youtube import paths
from youtube.model.file_extension import FileExtension
from youtube.paths import WATCHERS_DOWNLOAD_PATH, FILES_VIDEO_ARCHIVE_PATH, FILES_AUDIO_ARCHIVE_PATH
from youtube.utils import db_utils, playlist_utils, media_utils, constants
from youtube.watchers.youtube.api import YoutubeWorker
from youtube.watchers.youtube.media import YoutubeVideo, YoutubeVideoList


def alter_db_kv():
    files = file.list_files(paths.DB_PATH)

    for item in files:
        db_file = item.get_abs_path()
        ic(db_file)

        videos_list = YoutubeVideoList.from_file(db_file)

        # change DB keys and values

        # videos_list.write(db_file)


def update_channel_kv():
    items = [
        ("AmbientMusicalGenre", "Ambient"),
    ]
    for old_name, new_name in items:
        old_db_file = f"{paths.DB_PATH}\\{old_name}.txt"
        new_db_file = f"{paths.DB_PATH}\\{new_name}.txt"

        print(old_db_file, new_db_file)
        if old_name != new_name:
            print(f"To rename: {old_name} to {new_name}")

        videos_list = YoutubeVideoList.from_file(old_db_file)

        for video in videos_list.videos:
            video.channel_name = new_name
            video.file_name = video.generate_file_name()

        videos_list.write(new_db_file)


def get_yt_video_info():
    dk_file = paths.API_KEY_PATH
    worker = YoutubeWorker(dk_file)
    video_ids = ["vod6bKSBBh8"]
    ic(worker.get_videos(video_ids))


def shift_db():
    db_file = "E:\\Coding\\Projects\\Kevolehc\\Kevolehc\\youtube\\files\\_db\\ThePrimeThanatos.txt"
    video_id = "ulARBhWUpA8"
    # db_utils.move_video_number(db_file, video_id, 1496)
    # db_utils.shift_number(db_file, 174, -1)
    db_utils.delete(db_file, [video_id])


def shift_playlist():
    playlist_file = "E:\\Google Drive\\Mu\\plist\\GameChops.txt"
    video_url = constants.DEFAULT_YOUTUBE_WATCH + "ulARBhWUpA8"
    # playlist_utils.move_video_number(playlist_file, video_url, 367)
    playlist_utils.shift(playlist_file, 1289, -1)
    # playlist_utils.delete(playlist_file, [video_url])


def sync_media():
    watcher_name = "ThePrimeThanatos"
    ext = FileExtension.MP3
    db_file = f"E:\\Coding\\Projects\\Kevolehc\\Kevolehc\\youtube\\files\\_db\\{watcher_name}.txt"
    media_paths = [
        WATCHERS_DOWNLOAD_PATH + "\\" + watcher_name,
        FILES_AUDIO_ARCHIVE_PATH + "\\" + watcher_name,
        FILES_VIDEO_ARCHIVE_PATH + "\\" + watcher_name
    ]
    media_paths = list(filter(lambda p: file.dir_exists(p), media_paths))
    media_utils.sync_media_filenames_with_db(db_file, media_paths, ext)


def db_to_list():
    for db_file in file.list_files("E:\\Coding\\Projects\\Kevolehc\\Kevolehc\\youtube\\files\\tests\\test_sync_media"):
        db_file_path = db_file.get_abs_path()
        db_data = file.read_json(db_file_path)

        videos = [YoutubeVideo.from_dict(v) for v in db_data.values()]
        videos = sorted(videos, key=lambda video: video.number)

        db_data = [v.to_dict() for v in videos]
        file.write_json(db_file_path, db_data)


#######################################################################################################################
# Main function
#######################################################################################################################
def __main__():
    # shift_db()
    alter_db_kv()
    # sync_media()
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
