from __future__ import unicode_literals
import os
import time
from utils import File
from youtube import paths
from youtube.model.file_extension import FileExtension
from youtube.model.file_tags import FileTags
from youtube.watchers.youtube.media import YoutubeVideo
from youtube.paths import WATCHERS_DOWNLOAD_PATH
from youtube.utils.ffmpeg import Ffmpeg
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


def shift_playlist_at_position(monitor_name, position, step):
    # TODO - YOUTUBE_PLAYLIST_PATH should not be used. Delete after making class for playlist
    playlist_location = paths.YOUTUBE_PLAYLIST_PATH
    playlist_file = '\\'.join([playlist_location, monitor_name + ".txt"])
    data = File.read(playlist_file, File.ENCODING_UTF8)

    for i in range(len(data)):
        line = data[i]
        if "[" in line[1:2]:
            track_nr = int(line[167:])
            if track_nr >= position:
                next_track_nr = track_nr + step
                data[i] = line[:167] + str(next_track_nr)

    File.write(playlist_file, data, File.ENCODING_UTF8)


def sync_pos_files_lib_with_db(monitor_name: str, lib_path: str, extension: FileExtension):
    db_file = '\\'.join([paths.DB_PATH, monitor_name + ".txt"])
    db_data = File.read_json(db_file)

    # Get all files in the directory
    files_list = File.list_files(lib_path)

    for element in files_list:
        filename = element[File.FILENAME]
        file_path = element[File.PATH]
        if filename.endswith(extension.value):
            file_abs_path = file_path + "\\" + filename
            tags = Ffmpeg.metadata_to_json(Ffmpeg.get_metadata(file_abs_path))
            file_id = tags.get(FileTags.DISC)
            if file_id is None:
                raise ValueError(f"File has no ID: {file_abs_path}")

            db_item_data = db_data.get(file_id)
            db_item_position = db_item_data[YoutubeVideo.NUMBER]
            file_position = int(tags.get(FileTags.TRACK))
            if file_position != db_item_position:
                if db_item_data is None:
                    raise ValueError(f"File not found in DB: {file_abs_path}")

                tags = {
                    FileTags.TRACK: str(db_item_position)
                }
                Ffmpeg.add_tags(file_abs_path, tags)

                new_file_name = file_path + "\\" + db_item_data[YoutubeVideo.FILE_NAME] + "." + extension.value
                os.rename(file_abs_path, new_file_name)


#######################################################################################################################
# Main function
#######################################################################################################################
def __main__():
    pass
    # -------===========------
    # check_db_integrity()
    # -------===========------
    # POSITION NUMBER IS INCLUSIVE!
    position_number = 1272
    monitor_name = "GameChops"
    # shift_db_at_position(monitor_name, position_number, -1)
    # -------===========------
    # shift_playlist_at_position(monitor_name, position_number, -1)
    # -------===========------
    # Gets track number from the DB file
    lib_path = "G:\\Music\\YT_Monitors\\" + monitor_name
    # sync_pos_files_lib_with_db(monitor_name, lib_path, constants.MP3)
    dl_lib_path = WATCHERS_DOWNLOAD_PATH + "\\" + monitor_name
    # sync_pos_files_lib_with_db(monitor_name, dl_lib_path, constants.MP3)
    # -------===========------
    # download_db_missing()
    # -------===========------


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