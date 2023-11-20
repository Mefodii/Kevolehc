from typing import Self

from utils import file
from youtube.utils.constants import DEFAULT_YOUTUBE_WATCH
from youtube.watchers.youtube.media import YoutubeVideo

START_POS_ITEM_FLAG = 0
START_POS_TITLE = 5
START_POS_URL = 115
START_POS_TRACK_NR = 167

ITEM_FLAG_DEFAULT = " [ ]"
ITEM_FLAG_MISSING = " [@]"

DUMMY = "!DUMMY!"


class PlaylistItem:
    def __init__(self, title: str, url: str, item_flag: str, track_nr: int = None):
        self.title = title
        self.url = url
        self.item_flag = item_flag
        self.track_nr = track_nr
        # Note: currently no special handling for children.
        # Every line which is under this item and until next PlaylistItem is considered as child.
        self.children: list[str] = []
        self.is_dummy = True if title == DUMMY else False

    @classmethod
    def from_youtubevideo(cls, item: YoutubeVideo):
        item_flag = ITEM_FLAG_DEFAULT if file.exists(item.get_file_abs_path()) else ITEM_FLAG_MISSING
        url = DEFAULT_YOUTUBE_WATCH + item.video_id
        obj = PlaylistItem(item.title, url, item_flag, item.number)
        return obj

    @classmethod
    def from_str(cls, line: str):
        item_flag = line[START_POS_ITEM_FLAG:START_POS_TITLE].rstrip()
        title = line[START_POS_TITLE:START_POS_URL].rstrip()
        url = line[START_POS_URL:START_POS_TRACK_NR].rstrip()
        track_nr = int(line[START_POS_TRACK_NR:].rstrip()) if len(line) > START_POS_TRACK_NR else None
        obj = PlaylistItem(title, url, item_flag, track_nr)
        return obj

    @classmethod
    def dummy(cls):
        return PlaylistItem(DUMMY, "", "")

    @classmethod
    def from_file(cls, playlist_file: str) -> list[Self]:
        playlist_data = file.read(playlist_file, file.ENCODING_UTF8)

        items = []
        item = None
        for line in playlist_data:
            if PlaylistItem.is_playlist_str(line):
                item = PlaylistItem.from_str(line)
                items.append(item)
            else:
                if not item:
                    item = PlaylistItem.dummy()
                    items.append(item)

                item.append_child(line)

        return items

    @classmethod
    def write(cls, playlist_file: str, items: list[Self]):
        """
        Write to playlist_file string representation of all items
        :param playlist_file:
        :param items:
        :return:
        """
        res = []
        for item in items:
            if not item.is_dummy:
                res.append(str(item))

            [res.append(child) for child in item.children]
        file.write(playlist_file, res, file.ENCODING_UTF8)

    @staticmethod
    def is_playlist_str(line: str) -> bool:
        # Keeping it simple atm
        return line[1:2] in "[{"

    def append_child(self, child: str):
        self.children.append(child)

    def __str__(self):
        if self.is_dummy:
            return DUMMY

        s = "".ljust(START_POS_ITEM_FLAG) + self.item_flag
        s = s.ljust(START_POS_TITLE) + self.title
        s = s.ljust(START_POS_URL) + self.url

        if self.track_nr is not None:
            s = s.ljust(START_POS_TRACK_NR) + str(self.track_nr)
        return s
