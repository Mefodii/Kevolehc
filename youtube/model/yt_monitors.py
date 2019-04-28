from youtube.utils import yt_datetime


class YoutubeMonitor:
    def __init__(self, data_string):
        object_elements = data_string.split(";")

        if len(object_elements) != 5:
            print("Incorrect declaration of " + data_string)

        self.name = object_elements[0]
        self.id = object_elements[1]
        self.reference_date = object_elements[2]
        self.video_number = object_elements[3]
        self.format = object_elements[4]

        self.videos = []
        self.check_date = None

        self.validate()

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

    def validate_format(self):
        pass

    def append_video(self, yt_video):
        self.videos.append(yt_video)

    def __repr__(self):
        return ";".join([self.name, self.id, self.reference_date, self.video_number, self.format])
