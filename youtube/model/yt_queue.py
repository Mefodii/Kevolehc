from ..utils.constants import DEFAULT_YOUTUBE_WATCH
from ..utils.file_names import replace_restricted_file_chars, replace_unicode_chars

INFO_DICT = "info_dict"


class YoutubeQueue:
    def __init__(self, video_id, file_name, save_location, save_format, video_quality=None, link=None):
        self.video_id = video_id
        self.file_name = normalize_file_name(file_name)
        self.save_location = save_location
        self.save_format = save_format
        self.link = link
        self.video_quality = video_quality

        if not link:
            self.link = DEFAULT_YOUTUBE_WATCH + self.video_id

        self.audio_dl_stats = None
        self.video_dl_stats = None

    def __repr__(self):
        return ";".join([self.video_id, self.link, self.file_name, self.save_location, self.save_format])

    def replace_file_name_tags(self):
        file_name = self.file_name
        for key, value in self.video_dl_stats.get(INFO_DICT).items():
            tag = f"%({key})s"
            if tag in file_name:
                file_name = file_name.replace(tag, value)
        if file_name != self.file_name:
            self.file_name = normalize_file_name(file_name)


def normalize_file_name(video_title):
    return replace_restricted_file_chars(video_title)
