from __future__ import annotations
from typing import TYPE_CHECKING, Self

from utils import file
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
PLAYLIST_FILE = "playlist_file"
DOWNLOAD = "download"

DUMMY_NAME = "dummy_name"

MANDATORY_FIELDS = [
    WATCHER_NAME,
    CHANNEL_ID,
    FILE_EXTENSION,
    CHECK_DATE,
    VIDEO_COUNT,
    DOWNLOAD,
]


class YoutubeWatcher:
    def __init__(self, name: str, channel_id: str, check_date: str, video_count: int, file_extension: FileExtension,
                 download: bool, playlist_file: str = None, video_quality: int = None):
        self.is_dummy = name == DUMMY_NAME

        if " " in name:
            raise ValueError(f"Space not allowed in name. Name: {name}")

        self.name = name
        self.channel_id = channel_id
        self.check_date = check_date
        self.video_count = video_count
        self.file_extension = file_extension
        self.download = download

        if self.file_extension.is_audio() and playlist_file is None and not self.is_dummy:
            raise Exception(f"Playlist file expected for watcher: {self.name}")

        self.playlist_file = playlist_file
        self.video_quality = video_quality

        self.save_location = "\\".join([paths.WATCHERS_DOWNLOAD_PATH, self.name])
        self.db_file = "\\".join([paths.DB_PATH, self.name + ".txt"])

        self.videos: list[YoutubeVideo] = []
        self.new_check_date = None

    @classmethod
    def dummy(cls) -> Self:
        obj = YoutubeWatcher(DUMMY_NAME, "dummy", "", 0, FileExtension.MP3,
                             True, None, None)
        return obj

    @staticmethod
    def validate_data(data: dict):
        for field in MANDATORY_FIELDS:
            if data.get(field) is None:
                raise ValueError(field + " not found")

    def append_video(self, yt_video: YoutubeVideo) -> None:
        self.videos.append(yt_video)

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        YoutubeWatcher.validate_data(data)

        name = data.get(WATCHER_NAME)
        channel_id = data.get(CHANNEL_ID)
        check_date = data.get(CHECK_DATE, yt_datetime.get_default_ytdate())
        video_count = data.get(VIDEO_COUNT, 0)
        file_extension: FileExtension = FileExtension.from_str(data.get(FILE_EXTENSION))
        playlist_file = data.get(PLAYLIST_FILE)
        download = data.get(DOWNLOAD)
        video_quality = data.get(VIDEO_QUALITY, None)

        obj = YoutubeWatcher(name, channel_id, check_date, video_count, file_extension,
                             download, playlist_file, video_quality)
        return obj

    @classmethod
    def from_file(cls, file_path: str) -> list[Self]:
        data = file.read_json(file_path)
        watchers = [YoutubeWatcher.from_dict(watcher_dict) for watcher_dict in data]
        return watchers

    def to_json(self) -> str:
        json_data = ""
        json_data += f" {{ "
        json_data += f"\"{WATCHER_NAME}\": \"{self.name}\", "
        json_data += f"\"{CHANNEL_ID}\": \"{self.channel_id}\", "
        json_data += f"\"{CHECK_DATE}\": \"{self.check_date}\", "
        json_data += f"\"{VIDEO_COUNT}\": {self.video_count}, "
        json_data += f"\"{FILE_EXTENSION}\": \"{self.file_extension.value}\", "
        json_data += f"\"{DOWNLOAD}\": {str(self.download).lower()}"
        if self.video_quality:
            json_data += f", \"{VIDEO_QUALITY}\": {self.video_quality}"
        if self.playlist_file:
            json_data += f", \"{PLAYLIST_FILE}\": \"{self.playlist_file}\""
        json_data += f" }}"

        return json_data

    def __repr__(self):
        return ";".join([self.name, self.channel_id, self.check_date, str(self.video_count), self.file_extension.value])
