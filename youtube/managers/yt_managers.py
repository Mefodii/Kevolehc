from __future__ import unicode_literals

from utils import File
from ..model.yt_monitors import YoutubeMonitor
from ..model.yt_video import YoutubeVideo
from ..model.yt_queue import YoutubeQueue
from ..utils import yt_datetime, constants
from .. import paths

from .ffmpeg import Ffmpeg

import youtube_dl


class MonitorManager:
    def __init__(self, monitors_file, api_worker, log_file):
        self.log_file = log_file
        self.api = api_worker
        self.db = monitors_file
        data = File.get_file_lines(self.db)

        self.header = data[0]

        self.monitors = []
        for i in range(1, len(data)):
            monitor = YoutubeMonitor(data[i])
            monitor = self.validate_id(monitor)
            self.monitors.append(monitor)

    def __repr__(self):
        return "\n".join([self.header] + [repr(monitor) for monitor in self.monitors])

    def validate_id(self, monitor):
        if not monitor.id:
            response = self.api.get_channel_id_from_name(monitor.name)
            monitor.id = response.get('items')[0].get('id')

        return monitor

    def log(self, message):
        File.append_to_file(self.log_file, message)

    def check_for_updates(self):
        self.log(str(yt_datetime.get_current_ytdate()) + " - starting update process for monitors")
        for monitor in self.monitors:
            monitor.check_date = yt_datetime.get_current_ytdate()
            response = self.api.get_channel_uploads_from_date(monitor.id, monitor.reference_date)

            # The search returns the video which is equals to reference date.
            if response and response[-1].get("snippet").get("publishedAt") == monitor.reference_date:
                response.pop()

            # Search results also contains playlist and channel.
            self.log(monitor.name + " - New uploads from last check - " + str(len(response)))
            videos = []
            for upload in response:
                if upload.get("id").get("kind") == "youtube#video":
                    videos.append(upload)
            videos = videos[::-1]

            self.log(monitor.name + " - New videos from last check - " + str(len(videos)))
            for item in videos:
                self.log("\t-\t" + str(item))
                yt_video = YoutubeVideo(item, monitor.video_number)

                monitor.video_number += 1
                monitor.append_video(yt_video)

    def append_tags(self):
        for monitor in self.monitors:
            for video in monitor.videos:
                file_abs_path = File.get_file_name_with_extension(video.save_location, video.file_name)
                file_extension = file_abs_path.split(".")[-1]

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

                Ffmpeg.add_tags(file_abs_path, tags)

    def finish(self):
        updated_data = [self.header]
        for monitor in self.monitors:
            monitor.reference_date = monitor.check_date
            updated_data.append(repr(monitor))
        File.write_lines_to_file_utf8(self.db, updated_data)


class YoutubeQueueManager:
    def __init__(self):
        self.queue_list = []

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
        [self.generate_queue_from_monitor(monitor) for monitor in monitor_manager.monitors]
        for queue in self.queue_list:
            YoutubeDownloader.download(queue)


class YoutubeDownloader:
    class YoutubeDownloaderLogger(object):
        def debug(self, msg):
            pass

        def warning(self, msg):
            print(msg)

        def error(self, msg):
            print(msg)

    @staticmethod
    def my_hook(d):
        if d['status'] == 'finished':
            print('Done downloading, now converting ...')

    @staticmethod
    def download(queue):
        if queue.save_format == "A":
            YoutubeDownloader.download_audio(queue)
        if queue.save_format == "V":
            YoutubeDownloader.download_video(queue)

    @staticmethod
    def download_audio(queue):
        ydl_opts = {
            'format': 'bestaudio/best',
            'ffmpeg_location': paths.RESOURCES_PATH,
            'outtmpl': queue.save_location + '\\' + queue.file_name + '.%(ext)s',
            'logger': YoutubeDownloader.YoutubeDownloaderLogger(),
            'progress_hooks': [YoutubeDownloader.my_hook],
            'postprocessors': [{'key': 'FFmpegExtractAudio',
                                'preferredcodec': 'mp3',
                                'preferredquality': '192'}],
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([queue.link])

    @staticmethod
    def download_video(queue):
        default_audio_name = "audio"
        default_video_name = "video"
        audio_file = queue.save_location + "\\" + default_audio_name
        video_file = queue.save_location + "\\" + default_video_name

        ydl_opts = {
            'format': 'bestaudio/best',
            'ffmpeg_location': paths.RESOURCES_PATH,
            'outtmpl': audio_file + '.%(ext)s',
            'logger': YoutubeDownloader.YoutubeDownloaderLogger(),
            'progress_hooks': [YoutubeDownloader.my_hook],
            'postprocessors': [{'key': 'FFmpegExtractAudio',
                                'preferredcodec': 'm4a',
                                'preferredquality': '192'},
                               {'key': 'FFmpegMetadata'}],
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([queue.link])

        ydl_opts = {
            'format': '137',
            'ffmpeg_location': paths.RESOURCES_PATH,
            'outtmpl': video_file + '.%(ext)s',
            'logger': YoutubeDownloader.YoutubeDownloaderLogger(),
            'progress_hooks': [YoutubeDownloader.my_hook]
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([queue.link])

        audio_file = default_audio_name + "." + constants.M4A
        video_file = default_video_name + "." + constants.MP4
        merged_file = queue.file_name + "." + constants.MERGED_FORMAT

        Ffmpeg.merge_audio_and_video(queue.save_location, audio_file, video_file, merged_file)
