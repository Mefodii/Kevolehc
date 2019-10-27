from __future__ import unicode_literals
import os
import sys
import time
from utils import File
from youtube import paths
from youtube.managers.yt_managers import MonitorManager, YoutubeQueueManager, YoutubeVideo, YoutubeQueue
from youtube.yt_api.requests import YoutubeWorker
from youtube.utils import yt_datetime


def prepare_videos(manager, monitor, reference_date):
    response = manager.api.get_channel_uploads_from_date(monitor.id, reference_date)

    # Search results also contains playlist and channel.
    videos = MonitorManager.filter_valid_videos(response)
    # Response videos are not sorted by date. Need to do that.
    videos = MonitorManager.sort_by_date(videos)

    for item in videos:
        yt_video_params = YoutubeVideo.parse_json_yt_response(item)
        yt_video = YoutubeVideo(yt_video_params[YoutubeVideo.ID], yt_video_params[YoutubeVideo.TITLE],
                                yt_video_params[YoutubeVideo.PUBLISHED_AT],
                                yt_video_params[YoutubeVideo.CHANNEL_NAME], 0)

        file_name = " - ".join([str(yt_video.number), str(yt_video.channel_name), str(yt_video.title)])
        save_location = paths.MONITORS_FILES_PATH + "\\" + monitor.name

        queue = YoutubeQueue(yt_video.id, file_name, save_location, monitor.format)

        yt_video.file_name = queue.file_name
        yt_video.save_location = queue.save_location
        monitor.append_video(yt_video)


# Read all monitors and cross-check with db files.
# Add missing videos with "MISSING" status and Number = 0.
def check_db_integrity():
    monitors_db = '/'.join([paths.INPUT_FILES_PATH, paths.YOUTUBE_MONITOR_FILE2])
    dk_file = '/'.join([paths.INPUT_FILES_PATH, paths.YOUTUBE_DK_FILE])

    worker = YoutubeWorker(dk_file)
    manager = MonitorManager(monitors_db, worker, paths.YOUTUBE_API_LOG)
    for monitor in manager.monitors:
        default_reference_date = yt_datetime.get_default_ytdate()
        db_file = '\\'.join([paths.DB_LOG_PATH, monitor.name + ".txt"])
        db_json = File.get_json_data(db_file)

        prepare_videos(manager, monitor, default_reference_date)

        for video in monitor.videos:
            if db_json.get(video.id, None) is None:
                db_json[video.id] = {"STATUS": "MISSING", "TITLE": video.title, "PUBLISHED_AT": video.publishedAt,
                                     "FILE_NAME": video.file_name, "SAVE_LOCATION": video.save_location,
                                     "NUMBER": video.number, "CHANNEL_NAME": video.channel_name,
                                     "FORMAT": monitor.format}

        File.write_json_data(db_file, db_json)


def shift_db_at_position():
    monitor_name = "ExtraCreditz"
    position = 1008
    db_file = '\\'.join([paths.DB_LOG_PATH, monitor_name + ".txt"])
    db_json = File.get_json_data(db_file)

    for key, value in db_json.items():
        if value["NUMBER"] >= position:
            number = value["NUMBER"]
            next_number = number + 1
            value["FILE_NAME"] = value["FILE_NAME"].replace(str(number) + " - ", str(next_number) + " - ")
            value["NUMBER"] = next_number

    File.write_json_data(db_file, db_json)


def download_db_missing():
    monitors_db = '/'.join([paths.INPUT_FILES_PATH, paths.YOUTUBE_MONITOR_FILE2])
    dk_file = '/'.join([paths.INPUT_FILES_PATH, paths.YOUTUBE_DK_FILE])

    worker = YoutubeWorker(dk_file)
    manager = MonitorManager(monitors_db, worker, paths.YOUTUBE_API_LOG)
    for monitor in manager.monitors:
        db_file = '\\'.join([paths.DB_LOG_PATH, monitor.name + ".txt"])
        db_json = File.get_json_data(db_file)

        for key, value in db_json.items():
            if value["STATUS"] == "MISSING":
                yt_video = YoutubeVideo(key, value[YoutubeVideo.TITLE], value[YoutubeVideo.PUBLISHED_AT],
                                        value[YoutubeVideo.CHANNEL_NAME], value[YoutubeVideo.NUMBER])
                monitor.append_video(yt_video)

    queue_manager = YoutubeQueueManager(paths.YOUTUBE_API_LOG)
    queue_manager.process_monitor_manager(manager)

    manager.append_tags()
    manager.update_track_list_log()
    manager.update_db_log()


#######################################################################################################################
# Main function
#######################################################################################################################
def __main__():
    shift_db_at_position()


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