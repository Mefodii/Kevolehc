import re
from ..utils import constants


class YoutubeQueue:
    def __init__(self, video_id, file_name, save_location, save_format):
        self.video_id = video_id
        self.file_name = replace_restricted_file_chars(file_name)
        self.save_location = save_location
        self.save_format = save_format
        self.link = constants.DEFAULT_YOUTUBE_WATCH + self.video_id

    def __repr__(self):
        return ";".join([self.video_id, self.link, self.file_name, self.save_location, self.save_format])


def replace_restricted_file_chars(video_title):
    return re.sub('[' + re.escape(''.join(constants.RESTRICTED_CHARS)) + ']',
                  constants.DEFAULT_REPLACE_CHAR, video_title)
