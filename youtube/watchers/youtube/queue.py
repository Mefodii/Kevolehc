from youtube.model.file_extension import FileExtension
from youtube.utils.constants import DEFAULT_YOUTUBE_WATCH
from youtube.utils.file_names import normalize_file_name
from youtube.watchers.youtube.media import YoutubeVideo

INFO_DICT = "info_dict"


class YoutubeQueue:
    def __init__(self, video_id: str, file_name: str, save_location: str, file_extension: FileExtension,
                 video_quality: int = None, link: str = None):
        self.video_id = video_id
        self.file_name = normalize_file_name(file_name)
        self.save_location = save_location
        self.file_extension = file_extension
        self.link = link
        self.video_quality = video_quality

        if not link:
            self.link = DEFAULT_YOUTUBE_WATCH + self.video_id

        self.audio_dl_stats = None
        self.video_dl_stats = None

    @classmethod
    def from_youtubevideo(cls, video: YoutubeVideo):
        obj = cls(video.video_id, video.file_name, video.save_location, video.file_extension,
                  video.video_quality)
        return obj

    def get_file_abs_path(self):
        return f"{self.save_location}\\{self.file_name}.{self.file_extension.value}"

    def replace_file_name_tags(self):
        file_name = self.file_name
        for key, value in self.video_dl_stats.get(INFO_DICT).items():
            tag = f"%({key})s"
            if tag in file_name:
                file_name = file_name.replace(tag, value)
        if file_name != self.file_name:
            self.file_name = normalize_file_name(file_name)

    def __repr__(self):
        return ";".join([self.video_id, self.link, self.file_name, self.save_location, self.file_extension.value,
                         str(self.video_quality)])
