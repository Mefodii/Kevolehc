from __future__ import unicode_literals

from yt_dlp import DownloadError

from utils import file
from youtube.model.file_tags import FileTags
from youtube.model.playlist_item import PlaylistItem
from youtube.utils.ffmpeg import Ffmpeg
from youtube.utils.downloader import YoutubeDownloader
from youtube.paths import RESOURCES_PATH as FFMPEG_PATH
from youtube.utils import yt_datetime, db_utils

from youtube.watchers.youtube.media import YoutubeVideo
from youtube.watchers.youtube.queue import YoutubeQueue
from youtube.watchers.youtube.watcher import YoutubeWatcher

from youtube.watchers.youtube.api import YoutubeWorker


class YoutubeWatchersManager:
    def __init__(self, api_worker: YoutubeWorker, watchers_file: str = None, log_file: str = None):
        self.log_file = log_file
        self.api = api_worker
        self.watchers_file = watchers_file
        self.watchers: list[YoutubeWatcher] = YoutubeWatcher.from_file(watchers_file) if watchers_file else []
        self.queue_list: list[YoutubeQueue] = []
        self.processed_queue_list: list[YoutubeQueue] = []
        self.downloader = YoutubeDownloader(FFMPEG_PATH)

    # Add message to the log file
    def log(self, message, console_print: bool = False) -> None:
        if self.log_file is None:
            print(message)
        else:
            file.append(self.log_file, message)
            if console_print:
                print(message)

    def run_full(self) -> None:
        self.check_for_updates()
        self.generate_queue()
        self.download_queue()
        self.append_tags()
        self.update_playlist_log()
        self.update_db_log()
        self.finish()

    def simple_download(self, videos: list[YoutubeVideo]):
        dummy_watcher = YoutubeWatcher.dummy()
        dummy_watcher.videos = videos
        self.watchers.append(dummy_watcher)

        self.generate_queue()
        self.download_queue()
        self.append_tags()

    def check_db_integrity(self):
        # TODO - functionality to tested yet
        self.log(str(yt_datetime.get_current_ytdate()) + " - starting db integrity process", True)
        for watcher in self.watchers:
            self.log(f'Checking: {watcher.channel_id} - {watcher.name}', True)
            db_file = watcher.db_file
            db_videos = YoutubeVideo.from_db_file(db_file)

            self.obtain_all_videos(watcher)
            for video in watcher.videos:
                db_video = db_videos.get(video.video_id, None)
                # Check if video exists in db
                if db_video is None:
                    video.status = YoutubeVideo.STATUS_MISSING
                    db_videos[video.video_id] = video
                    self.log(f"Video missing: {video.to_dict()}", True)
                else:
                    # Add timestamp if missing
                    if db_video.published_at is None:
                        db_video.published_at = video.published_at

                    # Compare timestamp
                    if yt_datetime.compare_yt_dates(db_video.published_at, video.published_at) != 0:
                        message = f"{db_video.number} | API: {video.published_at} | DB: {db_video.published_at}"
                        self.log(message, True)
                        db_video.published_at = video.published_at

                    # Check and update video title in db if changed
                    if not db_video.title == video.title:
                        message = f"{db_video.number} | API: {video.title} | DB: {db_video.title}"
                        self.log(message, True)
                        db_video.title = video.title

                    db_videos[video.video_id] = db_video

            YoutubeVideo.write(db_file, db_videos)

    def download_db_missing(self):
        # TODO - functionality to tested yet
        for watcher in self.watchers:
            db_videos = YoutubeVideo.from_db_file(watcher.db_file)

            for db_video in db_videos.values():
                if db_video.status == YoutubeVideo.STATUS_MISSING:
                    # if db_video.status == YoutubeVideo.STATUS_UNABLE:
                    watcher.append_video(db_video)

        self.generate_queue()
        self.download_queue()
        self.append_tags()
        self.update_playlist_log()
        self.update_db_log()

    def obtain_all_videos(self, watcher: YoutubeWatcher):
        watcher.videos = []
        videos = self.api.get_channel_uploads_from_date(watcher.channel_id, yt_datetime.get_default_ytdate())
        for item in videos:
            yt_video = YoutubeVideo.from_youtube_api_video_and_watcher(item, watcher)
            yt_video.number = 0
            watcher.append_video(yt_video)

    def check_for_updates(self) -> None:
        self.log(str(yt_datetime.get_current_ytdate()) + " - starting update process for watchers")
        for watcher in self.watchers:
            self.log(f'Checking: {watcher.channel_id} - {watcher.name}')
            watcher.new_check_date = yt_datetime.get_current_ytdate()
            videos = self.api.get_channel_uploads_from_date(watcher.channel_id, watcher.check_date)

            self.log(f"{watcher.name.ljust(30)} || New uploads - {len(videos)}")
            for item in videos:
                self.log("\t" + str(item.data))
                watcher.video_count += 1
                yt_video = YoutubeVideo.from_youtube_api_video_and_watcher(item, watcher)
                watcher.append_video(yt_video)

    def generate_queue(self) -> None:
        self.log("Generating download queue")

        self.queue_list = []
        for watcher in self.watchers:
            for video in watcher.videos:
                queue = YoutubeQueue.from_youtubevideo(video)
                self.queue_list.append(queue)
                print(repr(queue))

    def download_queue(self):
        q_len = str(len(self.queue_list))

        self.processed_queue_list = []
        for i, queue in enumerate(self.queue_list, start=1):
            queue: YoutubeQueue
            q_progress = f"{i}/{q_len}"

            result_file = queue.get_file_abs_path()
            if file.exists(result_file):
                self.log(f"Queue ignored, file exist: {q_progress}", True)
            else:
                self.log(f"Process queue: {q_progress} - {result_file}", True)
                try:
                    self.downloader.download(queue)
                except DownloadError:
                    self.log(f"Unable to download - {queue.link}", True)

            self.processed_queue_list.append(queue)
        self.queue_list = []

    def append_tags(self) -> None:
        for watcher in self.watchers:
            for video in watcher.videos:
                tags = FileTags.extract_from_youtubevideo(video)

                file_abs_path = video.get_file_abs_path()
                if file.exists(file_abs_path):
                    Ffmpeg.add_tags(file_abs_path, tags, loglevel="error")

    def update_playlist_log(self) -> None:
        for watcher in self.watchers:
            playlist_file = watcher.track_log_file
            if playlist_file:
                track_list = [str(PlaylistItem.from_youtubevideo(video)) for video in watcher.videos]
                if len(track_list) > 0:
                    file.append(playlist_file, track_list)

    def update_db_log(self) -> None:
        [db_utils.add_videos(watcher) for watcher in self.watchers]

    def finish(self) -> None:
        for watcher in self.watchers:
            watcher.check_date = watcher.new_check_date

        watchers_json = ["[", ",\n".join([watcher.to_json() for watcher in self.watchers]), "]"]
        file.write(self.watchers_file, watchers_json, file.ENCODING_UTF8)
