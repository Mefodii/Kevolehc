from utils import file
from youtube.model.playlist_item import PlaylistItem
from youtube.utils import constants
from youtube.watchers.youtube.media import YoutubeVideo
from youtube.watchers.youtube.watcher import YoutubeWatcher


def shift_number(playlist_file: str, number: int, step: int = 1):
    """
    All videos with number greater or equal of given number will have its number changed by step.

    Update video file_name with new number
    :param playlist_file:
    :param number:
    :param step: how many position to shift. Negative as well
    :return:
    """
    playlist_items = read_playlist(playlist_file)
    shift_items(playlist_items, position_start=number, position_end=None, step=step)
    write_playlist(playlist_file, playlist_items)


def move_video_number(playlist_file: str, video_url: str, new_number: int):
    """
    Shift down by 1 all videos with number larger than video_id.number until reaching new_number.
    And set video_id.number to new_number

    If item.track_nr = 0, then shift by 1 all videos with number >= new_number

    Items file is sorted by track_nr
    :param playlist_file:
    :param video_url:
    :param new_number:
    :return:
    """
    playlist_items = read_playlist(playlist_file)
    if not is_sorted(playlist_items):
        raise Exception(f"Cannot move video. Playlist is not properly sorted by track_nr. File: {playlist_file}")

    item = find_item(playlist_items, video_url)
    playlist_items.remove(item)

    if item.track_nr == 0:
        shift_items(playlist_items, position_start=new_number, position_end=None, step=1)
    else:
        if item.track_nr > new_number:
            shift_items(playlist_items, position_start=new_number, position_end=item.track_nr, step=1)
        else:
            shift_items(playlist_items, position_start=item.track_nr, position_end=new_number, step=-1)

    item.track_nr = new_number
    inserted = False
    for i in range(len(playlist_items)):
        if playlist_items[i].track_nr > item.track_nr:
            playlist_items.insert(i, item)
            inserted = True
            break

    if not inserted:
        playlist_items.append(item)

    write_playlist(playlist_file, playlist_items)


def delete_video(playlist_file: str, video_url: str):
    """
    Find video with given id and delete it from file. All other videos number is shifted by -1.
    :param playlist_file:
    :param video_url:
    :return:
    """
    playlist_items = read_playlist(playlist_file)
    item = find_item(playlist_items, video_url)
    playlist_items.remove(item)

    shift_items(playlist_items, position_start=item.track_nr, position_end=None, step=-1)

    write_playlist(playlist_file, playlist_items)


def shift_items(items: list[PlaylistItem], position_start: int, position_end: int = None, step: int = 1):
    """
    All items within range position_start <= item.track_nr <= position_end will have its number changed by given step.

    Items are mutated with new position number and file_name
    :param items:
    :param position_start: video number start position; inclusive
    :param position_end: video number end position; inclusive
    :param step: how many position to shift. Negative as well
    :return:
    """
    for playlist_item in items:
        if (playlist_item.track_nr >= position_start and
                (position_end is None or (position_end and playlist_item.track_nr <= position_end))):
            playlist_item.track_nr += step
            if playlist_item.track_nr <= 0:
                raise Exception(f"Number <= 0 not allowed. Video ID: {playlist_item.url}")


def read_playlist(playlist_file: str) -> list[PlaylistItem]:
    """
    Read playlist_file and cast it to list of PlaylistItems
    :param playlist_file:
    :return:
    """
    playlist_data = file.read(playlist_file, file.ENCODING_UTF8)

    items = []
    item = None
    for line in playlist_data:
        if PlaylistItem.is_playlist_str(line):
            item = PlaylistItem.from_str(line)
            items.append(item)
        else:
            item.append_child(line)

    return items


def write_playlist(playlist_file: str, items: list[PlaylistItem]):
    """
    Write to playlist_file string representation of all items
    :param playlist_file:
    :param items:
    :return:
    """
    res = []
    for item in items:
        res.append(str(item))
        [res.append(child) for child in item.children]
    file.write(playlist_file, res, file.ENCODING_UTF8)


def add_missing_track_number(playlist_file: str, db_file: str):
    db_data = file.read_json(db_file)
    playlist_items = read_playlist(playlist_file)

    for item in playlist_items:
        if item.track_nr is None:
            video_id = item.url.replace(constants.DEFAULT_YOUTUBE_WATCH, "")
            video_dict = db_data[video_id]
            if video_dict is None:
                raise Exception(f"Video not found in DB. Video ID: {video_id}")

            video = YoutubeVideo.from_dict(video_dict)
            item.track_nr = video.number

    write_playlist(playlist_file, playlist_items)


def find_item(items: list[PlaylistItem], url: str) -> PlaylistItem | None:
    """
    :param items:
    :param url:
    :return: First PlaylistItem with given url. None if not found.
    """
    for i in range(len(items)):
        if items[i].url == url:
            return items[i]

    return None


def is_sorted(items: list[PlaylistItem]) -> bool:
    """
    :param items:
    :return: True if all items in list are sorted ascending by track_nr, no duplicates
    """
    for i in range(len(items) - 1):
        this_track_nr = items[i].track_nr
        next_track_nr = items[i+1].track_nr
        if this_track_nr is None or next_track_nr is None:
            return False
        if this_track_nr >= next_track_nr > 0:
            return False

    return True
