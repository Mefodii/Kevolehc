from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from youtube.watchers.youtube.media import YoutubeVideo

from youtube import paths
from youtube.utils import yt_datetime

# TODO - rename properties to correct snake_case
YOUTUBE_CHANNEL_USERNAME = "Youtube_Channel_Username"
YOUTUBE_CHANNEL_ID = "Youtube_Channel_ID"
REFERENCE_DATE = "Reference_Date"
LAST_VIDEO_NUMBER = "Last_Video_Number"
FORMAT = "Format"
VIDEO_QUALITY = "Video_Quality"
TRACK_LOG_FILE = "Track_log_file"

MANDATORY_FIELDS = [
    YOUTUBE_CHANNEL_USERNAME,
    YOUTUBE_CHANNEL_ID,
    REFERENCE_DATE,
    LAST_VIDEO_NUMBER,
    FORMAT
]


class YoutubeWatcher:
    def __init__(self, json_data: dict):
        # TODO - create a function "from_dict" and change init with arguments. Similar to YoutubeVideo
        self.name = json_data.get(YOUTUBE_CHANNEL_USERNAME)
        self.id = json_data.get(YOUTUBE_CHANNEL_ID)
        self.reference_date = YoutubeWatcher.init_reference_data(json_data.get(REFERENCE_DATE, None))
        self.video_number = YoutubeWatcher.init_video_number(json_data.get(LAST_VIDEO_NUMBER, None))
        self.format = json_data.get(FORMAT)
        self.track_log_file = json_data.get(TRACK_LOG_FILE, None)
        self.video_quality = YoutubeWatcher.init_video_quality(json_data.get(VIDEO_QUALITY, None))

        self.videos: list[YoutubeVideo] = []
        self.check_date = None
        self.save_location = "\\".join([paths.WATCHERS_DOWNLOAD_PATH, self.name])
        self.db_file = "\\".join([paths.DB_LOG_PATH, self.name + ".txt"])

    @staticmethod
    def validate_json(json_data: dict):
        for field in MANDATORY_FIELDS:
            if json_data.get(field, None) is None:
                raise ValueError(field + " not found")

    @staticmethod
    def init_reference_data(reference_date: str | None) -> str:
        if not reference_date:
            return yt_datetime.get_default_ytdate()

        return reference_date

    @staticmethod
    def init_video_number(video_number: str | int | None) -> int:
        if not video_number:
            return 1

        return int(video_number)

    @staticmethod
    def init_video_quality(video_quality: str | int | None) -> int | None:
        if video_quality:
            return int(video_quality)

        return None

    def append_video(self, yt_video: YoutubeVideo) -> None:
        self.videos.append(yt_video)

    def generate_default_track_log_file_name(self):
        return "\\".join([paths.WATCHERS_DOWNLOAD_PATH, self.name, self.name + ".txt"])

    def to_json(self) -> str:
        json_data = ""
        json_data += f" {{ "
        json_data += f"\"{YOUTUBE_CHANNEL_USERNAME}\": \"{self.name}\", "
        json_data += f"\"{YOUTUBE_CHANNEL_ID}\": \"{self.id}\", "
        json_data += f"\"{REFERENCE_DATE}\": \"{self.reference_date}\", "
        json_data += f"\"{LAST_VIDEO_NUMBER}\": {self.video_number}, "
        json_data += f"\"{FORMAT}\": \"{self.format}\""
        if self.video_quality:
            json_data += f", \"{VIDEO_QUALITY}\": \"{self.video_quality}\""
        if self.track_log_file:
            json_data += f", \"{TRACK_LOG_FILE}\": \"{self.track_log_file}\""
        json_data += f" }}"

        return json_data

    def __repr__(self):
        return ";".join([self.name, self.id, self.reference_date, str(self.video_number), self.format])
