from __future__ import unicode_literals

from utils import File
from youtube.model.yt_monitors import YoutubeMonitor
from youtube.model.yt_video import YoutubeVideo
from youtube.model.yt_queue import YoutubeQueue
from youtube.utils import yt_datetime
from youtube import paths

import youtube_dl
import os
import re


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
            file_name = str(video.number) + " - " + video.title
            save_location = paths.MONITORS_FILES_PATH + "\\" + monitor.name
            queue = YoutubeQueue(video.id, file_name, save_location, monitor.format)
            print(repr(queue))
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
            'outtmpl': queue.save_location + '/' + queue.file_name + '.%(ext)s',
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
        audio_file = queue.save_location + "\\audio"
        video_file = queue.save_location + "\\video"

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

        audio_file_full = audio_file + ".m4a"
        video_file_full = video_file + ".mp4"

        char_list = ['<', '>', ':', '\"', '/', '\\', '?', '*']
        merged_file = queue.save_location + '\\' + re.sub('[' + re.escape(''.join(char_list)) + ']', '#', queue.file_name) + ".mp4"
        temp_merged_file = queue.save_location + "\\merged.mp4"

        merge_command = "ffmpeg -i " + video_file_full + " -i " + audio_file_full + " -c:v copy -c:a copy " + temp_merged_file
        os.system(merge_command)
        os.remove(audio_file_full)
        os.remove(video_file_full)
        os.rename(temp_merged_file, merged_file)
