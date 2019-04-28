class YoutubeVideo:
    def __init__(self, json_data, video_number):
        self.id = json_data.get("id").get("videoId")
        self.title = json_data.get("snippet").get("title")
        self.publishedAt = json_data.get("snippet").get("publishedAt")
        self.number = video_number

    def __str__(self):
        return {"Id": self.id, "Number": self.number, "Title": self.title, "PublisedAt": self.publishedAt}