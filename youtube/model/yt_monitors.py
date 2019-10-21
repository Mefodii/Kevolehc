from youtube.utils import yt_datetime

YOUTUBE_CHANNEL_USERNAME = "Youtube_Channel_Username"
YOUTUBE_CHANNEL_ID = "Youtube_Channel_ID"
REFERENCE_DATE = "Reference_Date"
LAST_VIDEO_NUMBER = "Last_Video_Number"
FORMAT = "Format"

MANDATORY_FIELDS = [
    REFERENCE_DATE,
    LAST_VIDEO_NUMBER,
    FORMAT
]


class YoutubeMonitor:
    def __init__(self, json):

        self.name = json.get(YOUTUBE_CHANNEL_USERNAME)
        self.id = json.get(YOUTUBE_CHANNEL_ID)
        self.reference_date = json.get(REFERENCE_DATE)
        self.video_number = json.get(LAST_VIDEO_NUMBER)
        self.format = json.get(FORMAT)

        self.videos = []
        self.check_date = None

        self.validate()

    @staticmethod
    def validate_json(json):

        if len(json) != 5:
            raise ValueError("5 arguments expected")

        for field in MANDATORY_FIELDS:
            if json.get(field, None) is None:
                raise ValueError(field + " not found")

        if (json.get(YOUTUBE_CHANNEL_ID, None) or json.get(YOUTUBE_CHANNEL_USERNAME, None)) is None:
            raise ValueError(YOUTUBE_CHANNEL_ID + " either " + YOUTUBE_CHANNEL_USERNAME + " is expected")

    def validate(self):
        self.validate_name_and_id()
        self.validate_reference_date()
        self.validate_video_number()
        self.validate_format()

    def validate_name_and_id(self):
        pass

    def validate_reference_date(self):
        if not self.reference_date:
            self.reference_date = yt_datetime.get_default_ytdate()

    def validate_video_number(self):
        if not self.video_number:
            self.video_number = 1
        else:
            self.video_number = int(self.video_number)

    def validate_format(self):
        pass

    def append_video(self, yt_video):
        self.videos.append(yt_video)

    def to_json(self):
        return f" {{ " \
               f"\"{YOUTUBE_CHANNEL_USERNAME}\": \"{self.name}\", " \
               f"\"{YOUTUBE_CHANNEL_ID}\": \"{self.id}\", " \
               f"\"{REFERENCE_DATE}\": \"{self.reference_date}\", " \
               f"\"{LAST_VIDEO_NUMBER}\": {self.video_number}, " \
               f"\"{FORMAT}\": \"{self.format}\" " \
               f"}}"

    def __repr__(self):
        return ";".join([self.name, self.id, self.reference_date, str(self.video_number), self.format])
