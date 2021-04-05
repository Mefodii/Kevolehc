from __future__ import unicode_literals

from utils import File
from ..utils.constants import DEFAULT_YOUTUBE_WATCH
from ..model.yt_monitors import YoutubeMonitor
from ..model.yt_video import YoutubeVideo
from ..model.yt_queue import YoutubeQueue
from ..model.downloader import YoutubeDownloader
from ..utils import yt_datetime, constants
from .. import paths
from youtube_dl.utils import DownloadError

from .ffmpeg import Ffmpeg


class MonitorManager:
    def __init__(self, monitors_file, api_worker, log_file):
        self.log_file = log_file
        self.api = api_worker
        self.db = monitors_file
        data = File.get_json_data(self.db)

        self.monitors = []
        for monitor_json in data:
            YoutubeMonitor.validate_json(monitor_json)
            monitor = YoutubeMonitor(monitor_json)
            monitor = self.validate_id(monitor)
            self.monitors.append(monitor)

    # If monitor has no id: obtain id using monitor's name
    def validate_id(self, monitor):
        if not monitor.id:
            response = self.api.get_channel_id_from_name(monitor.name)
            monitor.id = response.get('items')[0].get('id')

        return monitor

    # Add message to the log file
    def log(self, message):
        File.append_to_file(self.log_file, message)

    def check_for_updates(self):
        self.log(str(yt_datetime.get_current_ytdate()) + " - starting update process for monitors")
        for monitor in self.monitors:
            monitor.check_date = yt_datetime.get_current_ytdate()
            response = self.api.get_channel_uploads_from_date(monitor.id, monitor.reference_date)

            # Search results also contains playlist and channel.
            videos = MonitorManager.filter_valid_videos(response)

            # Response videos are not sorted by date. Need to do that.
            videos = MonitorManager.sort_by_date(videos)

            head = monitor.name.ljust(30) + " || New uploads - " + str(len(response))
            self.log(head.ljust(70) + " || New videos - " + str(len(videos)))
            for item in videos:
                self.log("\t" + str(item))
                yt_video_params = YoutubeVideo.parse_json_yt_response(item)
                yt_video = YoutubeVideo(yt_video_params[YoutubeVideo.ID], yt_video_params[YoutubeVideo.TITLE],
                                        yt_video_params[YoutubeVideo.PUBLISHED_AT],
                                        yt_video_params[YoutubeVideo.CHANNEL_NAME], monitor.video_number)

                monitor.video_number += 1
                monitor.append_video(yt_video)

    @staticmethod
    def filter_valid_videos(response):
        videos = []
        for upload in response:
            if upload.get("snippet").get("resourceId").get("kind") == "youtube#video":
                videos.append(upload)

        return videos

    @staticmethod
    def sort_by_date(videos):
        return sorted(videos, key=lambda k: k['contentDetails']['videoPublishedAt'])

    def append_tags(self):
        for monitor in self.monitors:
            for video in monitor.videos:
                file_extension = monitor.format
                file_abs_path = "\\".join([video.save_location, video.file_name]) + "." + file_extension

                if file_extension == constants.MP3:
                    tags = {
                        "genre": video.channel_name,
                        "title": video.title,
                        "track": str(video.number),
                        "copyright": video.channel_name,
                        "disc": video.id,
                        "comment": "by Mefodii"
                    }
                else:
                    tags = {
                        "author": video.channel_name,
                        "title": video.title,
                        "track": str(video.number),
                        "copyright": video.channel_name,
                        "episode_id": video.id,
                        "comment": "by Mefodii"
                    }

                if File.exists(file_abs_path):
                    Ffmpeg.add_tags(file_abs_path, tags)

    def update_track_list_log(self):
        for monitor in self.monitors:
            if monitor.format == constants.MP3:
                track_list = []
                track_list_log_file = monitor.track_log_file
                if track_list_log_file is None:
                    track_list_log_file = paths.MONITORS_FILES_PATH + "\\" + monitor.name + "\\" + monitor.name + ".txt"

                for video in monitor.videos:
                    file_abs_path = "\\".join([video.save_location, video.file_name]) + "." + monitor.format
                    if File.exists(file_abs_path):
                        track_mark = " [ ] " + video.title
                    else:
                        track_mark = " [@] " + video.title
                    track_list.append(track_mark.ljust(115) + DEFAULT_YOUTUBE_WATCH + video.id.ljust(20) + str(video.number))

                if len(track_list) > 0:
                    File.append_to_file(track_list_log_file, track_list)

    def update_db_log(self):
        for monitor in self.monitors:
            db_file = '\\'.join([paths.DB_LOG_PATH, monitor.name + ".txt"])
            db_json = {}
            if File.exists(db_file):
                db_json = File.get_json_data(db_file)

            for video in monitor.videos:
                result_file = video.save_location + "\\" + video.file_name + "." + monitor.format
                file_status = "UNABLE"
                if File.exists(result_file):
                    file_status = "DOWNLOADED"

                db_json[video.id] = {"STATUS": file_status, "TITLE": video.title, "PUBLISHED_AT": video.publishedAt,
                                     "FILE_NAME": video.file_name, "SAVE_LOCATION": video.save_location,
                                     "NUMBER": video.number, "CHANNEL_NAME": video.channel_name,
                                     "FORMAT": monitor.format}

            File.write_json_data(db_file, db_json)

    def finish(self):
        for monitor in self.monitors:
            monitor.reference_date = monitor.check_date

        updated_data = ["[", ",\n".join([monitor.to_json() for monitor in self.monitors]), "]"]
        File.write_lines_to_file_utf8(self.db, updated_data)


class YoutubeQueueManager:
    def __init__(self, log_file):
        self.queue_list = []
        self.log_file = log_file

    def log(self, message):
        File.append_to_file(self.log_file, message)
        print(message)

    def add_queue(self, queue):
        self.queue_list.append(queue)

    def generate_queue_from_monitor(self, monitor):
        for video in monitor.videos:
            file_name = " - ".join([str(video.number), str(video.channel_name), str(video.title)])
            save_location = paths.MONITORS_FILES_PATH + "\\" + monitor.name

            queue = YoutubeQueue(video.id, file_name, save_location, monitor.format)
            print(repr(queue))

            video.file_name = queue.file_name
            video.save_location = queue.save_location

            self.add_queue(queue)

    def process_monitor_manager(self, monitor_manager):
        self.log("Generating download queue")
        [self.generate_queue_from_monitor(monitor) for monitor in monitor_manager.monitors]

        q_len = str(len(self.queue_list))
        i = 0
        for queue in self.queue_list:
            i += 1
            q_progress = str(i) + "/" + q_len

            result_file = queue.save_location + "\\" + queue.file_name + "." + queue.save_format
            if File.exists(result_file):
                self.log("Queue ignored, file exist: " + q_progress)
            else:
                self.log("Process queue: " + q_progress + " - " + result_file)
                try:
                    YoutubeDownloader.download(queue)
                except DownloadError:
                    self.log("Unable to download - " + queue.link)
