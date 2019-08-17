from ..utils.constants import DEFAULT_YOUTUBE_WATCH
from ..utils.file_names import replace_restricted_file_chars, replace_unicode_chars


class YoutubeQueue:
    def __init__(self, video_id, file_name, save_location, save_format):
        self.video_id = video_id
        self.file_name = normalize_file_name(file_name)
        self.save_location = save_location
        self.save_format = save_format
        self.link = DEFAULT_YOUTUBE_WATCH + self.video_id

    def __repr__(self):
        return ";".join([self.video_id, self.link, self.file_name, self.save_location, self.save_format])


def normalize_file_name(video_title):
    return replace_restricted_file_chars(video_title)
