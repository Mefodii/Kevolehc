from unicodedata import normalize
from ..utils.file_names import replace_unicode_chars


class YoutubeVideo:

    ID = "ID"
    TITLE = "TITLE"
    PUBLISHED_AT = "PUBLISHED_AT"
    CHANNEL_NAME = "CHANNEL_NAME"
    NUMBER = "NUMBER"
    FILE_NAME = "FILE_NAME"
    SAVE_LOCATION = "SAVE_LOCATION"

    def __init__(self, id, title, published_at, channel_name, number, file_name="", save_location=""):
        self.id = id
        self.title = title
        self.publishedAt = published_at
        self.channel_name = channel_name
        self.number = number
        self.file_name = file_name
        self.save_location = save_location

    @staticmethod
    def parse_json_yt_response(json_data):
        params = {
            YoutubeVideo.ID: json_data.get("snippet").get("resourceId").get("videoId"),
            YoutubeVideo.TITLE: replace_unicode_chars(normalize('NFC', json_data.get("snippet").get("title"))),
            YoutubeVideo.PUBLISHED_AT: json_data.get("snippet").get("publishedAt"),
            YoutubeVideo.CHANNEL_NAME: json_data.get("snippet").get("channelTitle"),
        }
        return params

    def __str__(self):
        return {YoutubeVideo.ID: self.id, YoutubeVideo.NUMBER: self.number, YoutubeVideo.TITLE: self.title,
                YoutubeVideo.PUBLISHED_AT: self.publishedAt}
