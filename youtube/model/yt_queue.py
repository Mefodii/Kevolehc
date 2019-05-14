import re
from ..utils import constants


class YoutubeQueue:
    def __init__(self, video_id, file_name, save_location, save_format):
        self.video_id = video_id
        self.file_name = normalize_file_name(file_name)
        self.save_location = save_location
        self.save_format = save_format
        self.link = constants.DEFAULT_YOUTUBE_WATCH + self.video_id

    def __repr__(self):
        return ";".join([self.video_id, self.link, self.file_name, self.save_location, self.save_format])


def normalize_file_name(video_title):
    first_phase = replace_restricted_file_chars(video_title)
    return replace_unicode_chars(first_phase)


def replace_unicode_chars(video_title):
    processed_title = video_title
    for chars in constants.NON_PARSED_CHARS:
        processed_title = processed_title.replace(chars[0], chars[1])

    return processed_title


def replace_restricted_file_chars(video_title):
    return re.sub('[' + re.escape(''.join(constants.RESTRICTED_CHARS)) + ']',
                  constants.DEFAULT_REPLACE_CHAR, video_title)
