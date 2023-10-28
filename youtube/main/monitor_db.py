from __future__ import unicode_literals
import os
import time
from utils import File
from youtube import paths
from youtube.watchers.youtube.media import YoutubeVideo
from youtube.paths import WATCHERS_DOWNLOAD_PATH
from youtube.utils.ffmpeg import Ffmpeg


# def prepare_videos(manager, monitor: YoutubeMonitor, reference_date):
#     videos = manager.api.get_channel_uploads_from_date(monitor.id, reference_date)
#
#     for item in videos:
#         data = item.data
#         yt_video_params = YoutubeVideo.parse_json_yt_response(data)
#         yt_video = YoutubeVideo(yt_video_params[YoutubeVideo.ID], yt_video_params[YoutubeVideo.TITLE],
#                                 yt_video_params[YoutubeVideo.PUBLISHED_AT],
#                                 yt_video_params[YoutubeVideo.CHANNEL_NAME], 0)
#
#         file_name = " - ".join([str(yt_video.number), str(yt_video.channel_name), str(yt_video.title)])
#         save_location = paths.WATCHERS_DOWNLOAD_PATH + "\\" + monitor.name
#
#         queue = YoutubeQueue(yt_video.id, file_name, save_location, monitor.format, monitor.video_quality)
#
#         yt_video.file_name = queue.file_name
#         yt_video.save_location = queue.save_location
#         monitor.append_video(yt_video)
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


def shift_db_at_position(monitor_name, position, step):
    db_file = '\\'.join([paths.DB_PATH, monitor_name + ".txt"])
    db_json = File.read_json(db_file)

    for key, value in db_json.items():
        if value["NUMBER"] >= position:
            number = value["NUMBER"]
            next_number = number + step
            value["FILE_NAME"] = value["FILE_NAME"].replace(str(number) + " - ", str(next_number) + " - ")
            value["NUMBER"] = next_number

    File.write_json(db_file, db_json)


def shift_playlist_at_position(monitor_name, position, step):
    playlist_location = "E:\\Google Drive\\Mu\\plist\\"
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


def sync_pos_files_lib_with_db(monitor_name, lib_path, extension):
    db_file = '\\'.join([paths.DB_PATH, monitor_name + ".txt"])
    db_json = File.read_json(db_file)

    # Get all files in the directory
    files_list = File.list_files_sub(lib_path)

    for element in files_list:
        if element["filename"].endswith(extension):
            abs_path = element["path"] + "\\" + element["filename"]
            metadata = Ffmpeg.metadata_to_json(Ffmpeg.get_metadata(abs_path))
            file_id = metadata.get("DISC", None)
            if file_id is None:
                raise ValueError("File has no ID: " + abs_path)

            json_info = db_json.get(file_id, None)
            position = json_info[YoutubeVideo.NUMBER]
            if int(metadata.get("TRACK")) != position:
                if json_info is None:
                    raise ValueError("File has no JSON: " + abs_path)

                tags = {
                    "track": str(position)
                }
                Ffmpeg.add_tags(abs_path, tags)

                new_name = element["path"] + "\\" + json_info[YoutubeVideo.FILE_NAME] + "." + extension
                os.rename(abs_path, new_name)


# def download_db_missing():
#     monitors_db = paths.YOUTUBE_WATCHERS_PATH
#     # monitors_db = paths.SIDE_MONITORS_PATH
#     # monitors_db = paths.SECONDARY_MONITORS_PATH
#     dk_file = paths.API_KEY_PATH
#
#     worker = YoutubeWorker(dk_file)
#     manager = MonitorManager(monitors_db, worker, paths.YOUTUBE_API_LOG)
#     for monitor in manager.monitors:
#         db_file = '\\'.join([paths.DB_LOG_PATH, monitor.name + ".txt"])
#         db_json = File.get_json_data(db_file)
#
#         for key, value in db_json.items():
#             if value["STATUS"] == "MISSING":
#             # if value["STATUS"] == "UNABLE":
#                 yt_video = YoutubeVideo(key, value[YoutubeVideo.TITLE], value[YoutubeVideo.PUBLISHED_AT],
#                                         value[YoutubeVideo.CHANNEL_NAME], value[YoutubeVideo.NUMBER])
#                 monitor.append_video(yt_video)
#
#     manager.generate_queue()
#     queue_manager = YoutubeQueueManager(paths.YOUTUBE_API_LOG)
#     queue_manager.queue_list = manager.queue_list
#     queue_manager.process_queue_list()
#
#     manager.append_tags()
#     manager.update_track_list_log()
#     manager.update_db_log()


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