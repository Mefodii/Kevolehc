from utils import File
from youtube.utils.constants import DEFAULT_YOUTUBE_WATCH
from youtube.watchers.youtube.media import YoutubeVideo

START_POS_ITEM_FLAG = 2
START_POS_TITLE = 6
START_POS_URL = 116
START_POS_TRACK_NR = 168

ITEM_FLAG_DEFAULT = "[ ]"
ITEM_FLAG_MISSING = "[@]"


class PlaylistItem:
    def __init__(self, title: str, track_nr: int, video_id: str, item_flag: str):
        self.title = title
        self.track_nr = track_nr
        self.video_id = video_id
        self.item_flag = item_flag
        self.children: list[str] = []

    @classmethod
    def from_youtubevideo(cls, item: YoutubeVideo):
        item_flag = ITEM_FLAG_DEFAULT if File.exists(item.get_file_abs_path()) else ITEM_FLAG_MISSING
        obj = PlaylistItem(item.title, item.number, item.video_id, item_flag)
        return obj

    @classmethod
    def from_str(cls, line: str):
        # TODO - create from string
        obj = PlaylistItem("", 0, "")
        return obj

    def append_child(self, child: str):
        self.children.append(child)

    def __str__(self):
        s = "".ljust(START_POS_ITEM_FLAG - 1) + self.item_flag
        s = s.ljust(START_POS_TITLE - 1) + self.title
        s = s.ljust(START_POS_URL - 1) + DEFAULT_YOUTUBE_WATCH + self.video_id
        s = s.ljust(START_POS_TRACK_NR - 1) + str(self.track_nr)
        return s
