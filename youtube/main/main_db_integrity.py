from __future__ import unicode_literals
import time

from icecream import ic

from utils import file
from utils.file import File
from youtube import paths
from youtube.model.file_extension import FileExtension
from youtube.paths import WATCHERS_DOWNLOAD_PATH
from youtube.utils import media_utils, playlist_utils

FILES_MAIN_PATH = paths.WATCHERS_DOWNLOAD_PATH
FILES_VIDEO_ARCHIVE_PATH = "G:\\Filme"
FILES_AUDIO_ARCHIVE_PATH = "G:\\Music\\yt_watchers"

DB_TO_IGNORE = [
    "TheNetNinja.txt"
]
#
#
# # Read all monitors and cross-check with db files.
# # Add missing videos with "MISSING" status and Number = 0.
# def check_db_integrity():
#     monitors_db = paths.YOUTUBE_WATCHERS_PATH
#     monitors_db = paths.YOUTUBE_WATCHERS_PGM_PATH
#     monitors_db = paths.YOUTUBE_WATCHERS2_PATH
#     dk_file = paths.API_KEY_PATH
#
#     worker = YoutubeWorker(dk_file)
#     manager = MonitorManager(monitors_db, worker, paths.YOUTUBE_API_LOG)
#     for monitor in manager.monitors:
#         default_reference_date = yt_datetime.get_default_ytdate()
#         db_file = '\\'.join([paths.DB_LOG_PATH, monitor.name + ".txt"])
#         db_json = File.get_json_data(db_file)
#
#         prepare_videos(manager, monitor, default_reference_date)
#
#         for video in monitor.videos:
#             db_video = db_json.get(video.video_id, None)
#             # Check if video exists in db
#             if db_video is None:
#                 db_json[video.video_id] = {"STATUS": "MISSING", "TITLE": video.title,
#                                            "PUBLISHED_AT": video.published_at,
#                                            "FILE_NAME": video.file_name, "SAVE_LOCATION": video.save_location,
#                                            "NUMBER": video.number, "CHANNEL_NAME": video.channel_name,
#                                            "FORMAT": monitor.format}
#                 print(db_json[video.video_id])
#             else:
#                 # Add timestamp if missing
#                 if db_video.get(YoutubeVideo.PUBLISHED_AT, None) is None:
#                     db_json[video.video_id][YoutubeVideo.PUBLISHED_AT] = video.published_at
#
#                 # Compare timestamp
#                 if compare_yt_dates(db_video.get(YoutubeVideo.PUBLISHED_AT), video.published_at) != 0:
#                     print(str(db_video.get(YoutubeVideo.NUMBER)), "API: ", video.published_at, "DB: ",
#                           db_video.get(YoutubeVideo.PUBLISHED_AT), sep=" | ")
#                     db_json[video.video_id][YoutubeVideo.PUBLISHED_AT] = video.published_at
#
#                 # Check and update video title in db if changed
#                 if not db_video.get(YoutubeVideo.TITLE) == video.title:
#                     print(str(db_video.get(YoutubeVideo.NUMBER)), video.title, db_video.get(YoutubeVideo.TITLE),
#                           sep=" | ")
#                     db_json[video.video_id][YoutubeVideo.TITLE] = video.title
#
#         File.write_json_data(db_file, db_json)


def validate_files_integrity():
    db_files = file.list_files(paths.DB_PATH)
    db_files: list[File] = list(filter(lambda f: f.name not in DB_TO_IGNORE, db_files))

    for db_file in db_files:
        file_name_no_ext = db_file.get_plain_name()
        media_paths = [
            FILES_MAIN_PATH + "\\" + file_name_no_ext,
            FILES_AUDIO_ARCHIVE_PATH + "\\" + file_name_no_ext,
            FILES_VIDEO_ARCHIVE_PATH + "\\" + file_name_no_ext
        ]

        media_paths = list(filter(lambda p: file.dir_exists(p), media_paths))
        media_utils.validate_files_integrity(db_file.get_abs_path(), media_paths)


#######################################################################################################################
# Main function
#######################################################################################################################
def __main__():
    validate_files_integrity()
    # db = "E:\\Coding\\Projects\\Kevolehc\\Kevolehc\\youtube\\files\\_db\\nyknullad.txt"
    # p = ["G:\\Music\\yt_watchers\\temp"]
    # media_utils.sync_media_filenames_with_db(db, p, FileExtension.MP3)
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