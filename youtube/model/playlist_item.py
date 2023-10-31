from utils import File
from youtube.utils.constants import DEFAULT_YOUTUBE_WATCH
from youtube.watchers.youtube.media import YoutubeVideo

START_POS_ITEM_FLAG = 0
START_POS_TITLE = 5
START_POS_URL = 115
START_POS_TRACK_NR = 167

ITEM_FLAG_DEFAULT = " [ ]"
ITEM_FLAG_MISSING = " [@]"


class PlaylistItem:
    def __init__(self, title: str, track_nr: int, url: str, item_flag: str):
        self.title = title
        self.track_nr = track_nr
        self.url = url
        self.item_flag = item_flag
        # Note: currently no special handling for children.
        # Every line which is under this item and until next PlaylistItem is considered as child.
        self.children: list[str] = []

    @classmethod
    def from_youtubevideo(cls, item: YoutubeVideo):
        item_flag = ITEM_FLAG_DEFAULT if File.exists(item.get_file_abs_path()) else ITEM_FLAG_MISSING
        url = DEFAULT_YOUTUBE_WATCH + item.video_id
        obj = PlaylistItem(item.title, item.number, url, item_flag)
        return obj

    @classmethod
    def from_str(cls, line: str):
        item_flag = line[START_POS_ITEM_FLAG:START_POS_TITLE].rstrip()
        title = line[START_POS_TITLE:START_POS_URL].rstrip()
        url = line[START_POS_URL:START_POS_TRACK_NR].rstrip()
        track_nr = int(line[START_POS_TRACK_NR:].rstrip())
        obj = PlaylistItem(title, track_nr, url, item_flag)
        return obj

    @staticmethod
    def is_playlist_str(line: str) -> bool:
        # Keeping it simple atm
        return line[1:2] in "[{"

    def append_child(self, child: str):
        self.children.append(child)

    def __str__(self):
        s = "".ljust(START_POS_ITEM_FLAG) + self.item_flag
        s = s.ljust(START_POS_TITLE) + self.title
        s = s.ljust(START_POS_URL) + self.url
        s = s.ljust(START_POS_TRACK_NR) + str(self.track_nr)
        return s
