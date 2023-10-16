from youtube.utils import yt_datetime

YOUTUBE_CHANNEL_USERNAME = "Youtube_Channel_Username"
YOUTUBE_CHANNEL_ID = "Youtube_Channel_ID"
REFERENCE_DATE = "Reference_Date"
LAST_VIDEO_NUMBER = "Last_Video_Number"
FORMAT = "Format"
VIDEO_QUALITY = "Video_Quality"
TRACK_LOG_FILE = "Track_log_file"

MANDATORY_FIELDS = [
    YOUTUBE_CHANNEL_USERNAME,
    YOUTUBE_CHANNEL_ID,
    REFERENCE_DATE,
    LAST_VIDEO_NUMBER,
    FORMAT
]


class YoutubeMonitor:
    def __init__(self, json_data: dict):

        self.name = json_data.get(YOUTUBE_CHANNEL_USERNAME)
        self.id = json_data.get(YOUTUBE_CHANNEL_ID)
        self.reference_date = json_data.get(REFERENCE_DATE)
        self.video_number = json_data.get(LAST_VIDEO_NUMBER)
        self.format = json_data.get(FORMAT)
        self.track_log_file = json_data.get(TRACK_LOG_FILE, None)
        self.video_quality = json_data.get(VIDEO_QUALITY, None)

        self.videos = []
        self.check_date = None

        self.validate()

    @staticmethod
    def validate_json(json_data: dict):
        for field in MANDATORY_FIELDS:
            if json_data.get(field, None) is None:
                raise ValueError(field + " not found")

    def validate(self):
        self.validate_reference_date()
        self.validate_video_number()
        self.validate_video_quality()

    def validate_reference_date(self):
        if not self.reference_date:
            self.reference_date = yt_datetime.get_default_ytdate()

    def validate_video_number(self):
        if not self.video_number:
            self.video_number = 1
        else:
            self.video_number = int(self.video_number)

    def validate_video_quality(self):
        if self.video_quality:
            self.video_quality = int(self.video_quality)

    def append_video(self, yt_video):
        self.videos.append(yt_video)

    def to_json(self):
        json = ""
        json += f" {{ "
        json += f"\"{YOUTUBE_CHANNEL_USERNAME}\": \"{self.name}\", "
        json += f"\"{YOUTUBE_CHANNEL_ID}\": \"{self.id}\", "
        json += f"\"{REFERENCE_DATE}\": \"{self.reference_date}\", "
        json += f"\"{LAST_VIDEO_NUMBER}\": {self.video_number}, "
        json += f"\"{FORMAT}\": \"{self.format}\""
        if self.video_quality:
            json += f", \"{VIDEO_QUALITY}\": \"{self.video_quality}\""
        if self.track_log_file:
            json += f", \"{TRACK_LOG_FILE}\": \"{self.track_log_file}\""
        json += f" }}"

        return json

    def __repr__(self):
        return ";".join([self.name, self.id, self.reference_date, str(self.video_number), self.format])
