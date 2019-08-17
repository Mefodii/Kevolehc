from unicodedata import normalize
from ..utils.file_names import replace_unicode_chars


class YoutubeVideo:
    def __init__(self, json_data, video_number):
        self.id = json_data.get("snippet").get("resourceId").get("videoId")
        self.title = replace_unicode_chars(normalize('NFKD', json_data.get("snippet").get("title")))
        self.publishedAt = json_data.get("snippet").get("publishedAt")
        self.channel_name = json_data.get("snippet").get("channelTitle")
        self.number = video_number
        self.file_name = ""
        self.save_location = ""

    def __str__(self):
        return {"Id": self.id, "Number": self.number, "Title": self.title, "PublisedAt": self.publishedAt}
