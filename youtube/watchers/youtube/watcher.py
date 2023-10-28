from __future__ import annotations
from typing import TYPE_CHECKING

from youtube.model.file_extension import FileExtension

if TYPE_CHECKING:
    from youtube.watchers.youtube.media import YoutubeVideo

from youtube import paths
from youtube.utils import yt_datetime

WATCHER_NAME = "watcher_name"
CHANNEL_ID = "channel_id"
CHECK_DATE = "check_date"
VIDEO_COUNT = "video_count"
FILE_EXTENSION = "file_extension"
VIDEO_QUALITY = "video_quality"
TRACK_LOG_FILE = "track_log_file"

MANDATORY_FIELDS = [
    WATCHER_NAME,
    CHANNEL_ID,
    FILE_EXTENSION
]


class YoutubeWatcher:
    def __init__(self, name: str, channel_id: str, check_date: str, video_count: int, file_extension: FileExtension,
                 track_log_file: str = None, video_quality: int = None):
        # TODO - need parameter to only track the uploads, without download
        self.name = name
        self.channel_id = channel_id
        self.check_date = check_date
        self.video_count = video_count
        self.file_extension = file_extension
        self.track_log_file = track_log_file
        self.video_quality = video_quality

        self.save_location = "\\".join([paths.WATCHERS_DOWNLOAD_PATH, self.name])
        self.db_file = "\\".join([paths.DB_PATH, self.name + ".txt"])

        self.videos: list[YoutubeVideo] = []
        self.new_check_date = None

    @staticmethod
    def validate_data(data: dict):
        for field in MANDATORY_FIELDS:
            if data.get(field) is None:
                raise ValueError(field + " not found")

    def append_video(self, yt_video: YoutubeVideo) -> None:
        self.videos.append(yt_video)

    def generate_default_track_log_file_name(self):
        return "\\".join([paths.WATCHERS_DOWNLOAD_PATH, self.name, self.name + ".txt"])

    @classmethod
    def from_dict(cls, data: dict):
        YoutubeWatcher.validate_data(data)

        name = data.get(WATCHER_NAME)
        channel_id = data.get(CHANNEL_ID)
        check_date = data.get(CHECK_DATE, yt_datetime.get_default_ytdate())
        video_count = data.get(VIDEO_COUNT, 0)
        file_extension: FileExtension = FileExtension.from_str(data.get(FILE_EXTENSION))
        track_log_file = data.get(TRACK_LOG_FILE)
        video_quality = data.get(VIDEO_QUALITY, None)

        obj = YoutubeWatcher(name, channel_id, check_date, video_count, file_extension, track_log_file, video_quality)
        return obj

    def to_json(self) -> str:
        json_data = ""
        json_data += f" {{ "
        json_data += f"\"{WATCHER_NAME}\": \"{self.name}\", "
        json_data += f"\"{CHANNEL_ID}\": \"{self.channel_id}\", "
        json_data += f"\"{CHECK_DATE}\": \"{self.check_date}\", "
        json_data += f"\"{VIDEO_COUNT}\": {self.video_count}, "
        json_data += f"\"{FILE_EXTENSION}\": \"{self.file_extension.value}\""
        if self.video_quality:
            json_data += f", \"{VIDEO_QUALITY}\": \"{self.video_quality}\""
        if self.track_log_file:
            json_data += f", \"{TRACK_LOG_FILE}\": \"{self.track_log_file}\""
        json_data += f" }}"

        return json_data

    def __repr__(self):
        return ";".join([self.name, self.channel_id, self.check_date, str(self.video_count), self.file_extension.value])
