from unicodedata import normalize

class YoutubeVideo:
    def __init__(self, json_data, video_number):
        self.id = json_data.get("id").get("videoId")
        self.title = normalize('NFKD', json_data.get("snippet").get("title"))
        self.publishedAt = json_data.get("snippet").get("publishedAt")
        self.channel_name = json_data.get("snippet").get("channelTitle")
        self.number = video_number
        self.file_name = ""
        self.save_location = ""

    def __str__(self):
        return {"Id": self.id, "Number": self.number, "Title": self.title, "PublisedAt": self.publishedAt}