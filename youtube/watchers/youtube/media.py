from typing import Self

from unicodedata import normalize

from utils import file
from youtube.model.file_extension import FileExtension
from youtube.utils.file_names import replace_unicode_chars, normalize_file_name
from youtube.watchers.youtube.watcher import YoutubeWatcher
from youtube.watchers.youtube.api import YoutubeAPIVideo


class YoutubeVideo:

    VIDEO_ID = "VIDEO_ID"
    TITLE = "TITLE"
    PUBLISHED_AT = "PUBLISHED_AT"
    CHANNEL_NAME = "CHANNEL_NAME"
    NUMBER = "NUMBER"
    FILE_NAME = "FILE_NAME"
    SAVE_LOCATION = "SAVE_LOCATION"
    STATUS = "STATUS"
    FILE_EXTENSION = "FILE_EXTENSION"
    VIDEO_QUALITY = "VIDEO_QUALITY"
    VIDEO_TYPE = "VIDEO_TYPE"

    STATUS_NO_STATUS = "NO_STATUS"
    STATUS_UNABLE = "UNABLE"
    STATUS_DOWNLOADED = "DOWNLOADED"
    STATUS_MISSING = "MISSING"
    STATUS_SKIP = "SKIP"

    TYPE_REGULAR = "TYPE_REGULAR"
    TYPE_SHORT = "TYPE_SHORT"
    TYPE_LIVESTREAM = "TYPE_LIVESTREAM"

    def __init__(self, video_id: str, title: str, channel_name: str, published_at: str, number: int,
                 save_location: str = None, file_extension: FileExtension = None, file_name: str = None,
                 video_quality: int = None, status: str = None):
        self.video_id = video_id
        self.title = replace_unicode_chars(normalize('NFC', title))
        self.channel_name = channel_name
        self.published_at = published_at
        self.number = number
        self.save_location = save_location

        self.file_name = file_name
        self.init_file_name()
        self.file_extension = file_extension
        self.video_quality = video_quality
        # TODO - extract type from api
        self.video_type = self.TYPE_REGULAR

        self.status = status if status else YoutubeVideo.STATUS_NO_STATUS

    @classmethod
    def from_youtube_api_video_and_watcher(cls, item: YoutubeAPIVideo, watcher: YoutubeWatcher) -> Self:
        video_id = item.get_id()
        title = item.get_title()
        channel_name = watcher.name
        published_at = item.get_publish_date()

        obj = cls(video_id, title, channel_name, published_at,
                  watcher.video_count, watcher.save_location,
                  file_extension=watcher.file_extension, file_name=None, video_quality=watcher.video_quality)
        return obj

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        video_id = data.get(YoutubeVideo.VIDEO_ID)
        title = data.get(YoutubeVideo.TITLE)
        channel_name = data.get(YoutubeVideo.CHANNEL_NAME)
        published_at = data.get(YoutubeVideo.PUBLISHED_AT)
        number = data.get(YoutubeVideo.NUMBER)
        file_extension = FileExtension.from_str(data.get(YoutubeVideo.FILE_EXTENSION))
        file_name = data.get(YoutubeVideo.FILE_NAME)
        video_quality = data.get(YoutubeVideo.VIDEO_QUALITY)
        status = data.get(YoutubeVideo.STATUS)

        obj = cls(video_id, title, channel_name, published_at, number, save_location=None,
                  file_extension=file_extension, file_name=file_name, video_quality=video_quality, status=status)
        return obj

    @classmethod
    def from_db_file(cls, db_file: str) -> dict[str, Self]:
        db_data = file.read_json(db_file)
        videos = {}
        for k in db_data:
            video = YoutubeVideo.from_dict(k)
            videos[video.video_id] = video
        return videos

    @classmethod
    def write(cls, db_file: str, videos: dict[str, Self]) -> None:
        videos_list: list[YoutubeVideo] = list(sorted(videos.values(), key=lambda v: v.number))
        db_data = [v.to_dict() for v in videos_list]
        file.write_json(db_file, db_data)

    def init_file_name(self) -> None:
        file_name = self.file_name
        if not file_name:
            file_name = self.generate_file_name()

        self.file_name = normalize_file_name(file_name)

    def generate_file_name(self) -> str:
        file_name = " - ".join([str(self.number), str(self.channel_name), str(self.title)])
        return normalize_file_name(file_name)

    def get_file_abs_path(self) -> str:
        return f"{self.save_location}\\{self.file_name}.{self.file_extension.value}"

    def to_dict(self):
        data = {
            YoutubeVideo.VIDEO_ID: self.video_id,
            YoutubeVideo.TITLE: self.title,
            YoutubeVideo.CHANNEL_NAME: self.channel_name,
            YoutubeVideo.PUBLISHED_AT: self.published_at,
            YoutubeVideo.NUMBER: self.number,
            YoutubeVideo.FILE_EXTENSION: self.file_extension.value,
            YoutubeVideo.FILE_NAME: self.file_name,
            YoutubeVideo.VIDEO_QUALITY: self.video_quality,
            YoutubeVideo.STATUS: self.status,
        }

        # Remove all keys with value None
        data = {k: v for k, v in data.items() if v is not None}
        return data

    def __str__(self):
        return str(self.to_dict())

    def __repr__(self):
        return str(self)


class YoutubeVideoList(list):
    # TODO (very low priority) - try to extend list functionality to mimic db_utils.py
    # https://realpython.com/inherit-python-list/#creating-list-like-classes-in-python
    pass
